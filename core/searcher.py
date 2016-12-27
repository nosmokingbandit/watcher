import datetime
import logging

import core
from core import newznab, scoreresults, snatcher, sqldb, updatestatus
from core.rss import predb

logging = logging.getLogger(__name__)


class Searcher():

    def __init__(self):
        self.nn = newznab.NewzNab()
        self.score = scoreresults.ScoreResults()
        self.sql = sqldb.SQL()
        self.predb = predb.PreDB()
        self.snatcher = snatcher.Snatcher()
        self.update = updatestatus.Status()

    # this only runs when scheduled. Only started by the user when changing search settings.
    def auto_search_and_grab(self):
        ''' Scheduled searcher and grabber.

        Runs search when scheduled. ONLY runs when scheduled.
        Runs in its own thread.

        Searches only for movies that are Wanted, Found,
            or Finished -- if inside user-set date range.

        Will grab movie if autograb is 'true' and
            movie is 'Found' or 'Finished'.

        Updates core.NEXT_SEARCH time

        Does not return
        '''

        interval = int(core.CONFIG['Search']['searchfrequency']) * 3600
        now = datetime.datetime.today().replace(second=0, microsecond=0)
        core.NEXT_SEARCH = now + datetime.timedelta(0, interval)

        today = datetime.date.today()
        keepsearching = core.CONFIG['Search']['keepsearching']
        keepsearchingdays = int(core.CONFIG['Search']['keepsearchingdays'])
        keepsearchingdelta = datetime.timedelta(days=keepsearchingdays)
        auto_grab = core.CONFIG['Search']['autograb']

        self.predb.check_all()
        logging.info('Running automatic search.')
        if keepsearching == 'true':
            logging.info('Search for finished movies enabled. Will search again for any movie that has finished in the last {} days.'.format(keepsearchingdays))
        movies = self.sql.get_user_movies()
        if not movies:
            return False

        '''
        Loops through all movies to search for any that require it.
        '''
        for movie in movies:
            imdbid = movie['imdbid']
            title = movie['title']
            status = movie['status']
            finisheddate = movie['finisheddate']

            if movie['predb'] != 'found':
                continue

            if status in ['Wanted', 'Found']:
                    logging.info(u'{} status is {}. Searching now.'.format(title, status))
                    self.search(imdbid, title)
                    continue

            if status == 'Finished' and keepsearching == 'true':
                logging.info(u'{} is Finished but Keep Searching is enabled. Checking if Finished date is less than {} days ago.'.format(title, keepsearchingdays))
                finisheddateobj = datetime.datetime.strptime(finisheddate, '%Y-%m-%d').date()
                if finisheddateobj + keepsearchingdelta >= today:
                    logging.info('{} finished on {}, searching again.'.format(title, finisheddate))
                    self.search(imdbid, title)
                    continue
                else:
                    logging.info(u'{} finished on {} and is not within the search window.'.format(title, finisheddate))
                    continue
            continue

        '''
        If autograb is enabled, loops through movies and grabs any appropriate releases.
        '''
        if auto_grab == 'true':
            logging.info('Running automatic snatcher.')
            # In case we found something we'll check this again.
            movies = self.sql.get_user_movies()
            if not movies:
                return False
            for movie in movies:
                status = movie['status']

                if status == 'Found':
                    logging.info(u'{} status is Found. Running automatic snatcher.'.format(title))
                    self.snatcher.auto_grab(imdbid)
                    continue

                if status == 'Finished' and keepsearching == 'true':
                    logging.info(u'{} status is Finished but Keep Searching is enabled. Checking if Finished date is less than {} days ago.'.format(title, keepsearchingdays))
                    if finisheddateobj + keepsearchingdelta >= today:
                        logging.info(u'{} finished on {}, checking for a better result.'.format(title, finisheddate))
                        self.snatcher.auto_grab(imdbid)
                        continue
                    else:
                        logging.info(u'{} finished on {} and is not within the snatch again window.'.format(title, finisheddate))
                        continue
                else:
                    continue

        logging.info('Autosearch complete.')
        return

    def search(self, imdbid, title):
        ''' Search indexers for releases
        :param imdbid: str imdb identification number (tt123456)
        :param title: str movie title and year (Movie Title 2016)

        Checks if guid matches entries in MARKEDRESULTS and
            sets status if found. Default status Available.

        Sends results to self.scoreresults(), then stores them in SEARCHRESULTS

        Returns Bool if movie is found.
        '''

        newznab_results = self.nn.search_all(imdbid)
        scored_results = self.score.score(newznab_results, imdbid, 'nzb')
        # TODO eventually add search for torrents

        # sets result status based off marked results table
        marked_results = self.sql.get_marked_results(imdbid)
        if marked_results:
            for result in scored_results:
                if result['guid'] in marked_results:
                    result['status'] = marked_results[result['guid']]

        if scored_results:
            if not self.store_results(scored_results, imdbid):
                return False

        if not self.update.movie_status(imdbid):
            logging.info('No acceptable results found for {}'.format(imdbid))
            return False

        return True

    def store_results(self, results, imdbid):
        ''' Stores search results in database.
        :param results: list of dicts of search results
        :param imdbid: str imdb identification number (tt123456)

        Checks if result exists in SEARCHRESULTS already and ignores them.
            This keeps it from overwriting the date_found

        Returns Bool on success/failure.
        '''

        logging.info('{} results found for {}. Storing results.'.format(len(results), imdbid))

        # This iterates through the new search results and submits only results we haven't already stored. This keeps it from overwriting the FoundDate
        kept_guids = []
        BATCH_DB_STRING = []
        existing_results = self.sql.get_search_results(imdbid)

        # get list of guids of existing results
        if existing_results:
            for res in existing_results:
                kept_guids.append(res['guid'])

        for result in results:
            # if result already exists in table ignore it
            if result['guid'] in kept_guids:
                continue
            else:
                DB_STRING = result
                DB_STRING['imdbid'] = imdbid
                DB_STRING['date_found'] = datetime.date.today()

                BATCH_DB_STRING.append(DB_STRING)

        if BATCH_DB_STRING:
            if self.sql.write_search_results(BATCH_DB_STRING):
                return True
            else:
                return False
        else:
            return True
