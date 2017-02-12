import datetime
import logging

import core
from core import newznab, scoreresults, snatcher, sqldb, updatestatus, torrent, proxy
from core.rss import predb

logging = logging.getLogger(__name__)


class Searcher():

    def __init__(self):
        self.nn = newznab.NewzNab()
        self.score = scoreresults.ScoreResults()
        self.sql = sqldb.SQL()
        self.predb = predb.PreDB()
        self.snatcher = snatcher.Snatcher()
        self.torrent = torrent.Torrent()
        self.update = updatestatus.Status()

    def auto_search_and_grab(self):
        ''' Scheduled searcher and grabber.

        Runs search when scheduled. ONLY runs when scheduled.
        Runs in its own thread.

        First checks for all movies on predb.

        Searches only for movies where predb == u'found'.

        Searches only for movies that are Wanted, Found,
            or Finished -- if inside user-set date range.

        Will grab movie if autograb is 'true' and
            movie is 'Found' or 'Finished'.

        Updates core.NEXT_SEARCH time

        Does not return
        '''

        interval = core.CONFIG['Search']['searchfrequency'] * 3600
        now = datetime.datetime.today().replace(second=0, microsecond=0)
        core.NEXT_SEARCH = now + datetime.timedelta(0, interval)

        today = datetime.date.today()
        keepsearching = core.CONFIG['Search']['keepsearching']
        keepsearchingdays = core.CONFIG['Search']['keepsearchingdays']
        keepsearchingdelta = datetime.timedelta(days=keepsearchingdays)
        auto_grab = core.CONFIG['Search']['autograb']

        self.predb.check_all()
        logging.info(u'Running automatic search.')
        if keepsearching is True:
            logging.info(u'Search for finished movies enabled. Will search again for any movie that has finished in the last {} days.'.format(keepsearchingdays))
        movies = self.sql.get_user_movies()
        if not movies:
            return False

        '''
        Loops through all movies to search for any that require it.
        '''
        for movie in movies:
            status = movie['status']
            if status == 'Disabled':
                continue

            imdbid = movie['imdbid']
            title = movie['title']
            finisheddate = movie['finished_date']
            year = movie['year']
            quality = movie['quality']

            if movie['predb'] != u'found':
                continue

            if status in ['Wanted', 'Found']:
                    logging.info(u'{} status is {}. Searching now.'.format(title, status))
                    self.search(imdbid, title, year, quality)
                    continue

            if status == u'Finished' and keepsearching is True:
                logging.info(u'{} is Finished but Keep Searching is enabled. Checking if Finished date is less than {} days ago.'.format(title, keepsearchingdays))
                finisheddateobj = datetime.datetime.strptime(finisheddate, '%Y-%m-%d').date()
                if finisheddateobj + keepsearchingdelta >= today:
                    logging.info(u'{} finished on {}, searching again.'.format(title, finisheddate))
                    self.search(imdbid, title, year, quality)
                    continue
                else:
                    logging.info(u'{} finished on {} and is not within the search window.'.format(title, finisheddate))
                    continue
            continue

        '''
        If autograb is enabled, loops through movies and grabs any appropriate releases.
        '''
        if auto_grab is True:
            logging.info(u'Running automatic snatcher.')
            keepsearchingscore = core.CONFIG['Search']['keepsearchingscore']
            # In case we found something we'll check this again.
            movies = self.sql.get_user_movies()
            if not movies:
                return False
            for movie in movies:
                status = movie['status']
                if status == 'Disabled':
                    continue
                imdbid = movie['imdbid']
                title = movie['title']
                year = movie['year']
                quality = movie['quality']

                if status == u'Found':
                    logging.info(u'{} status is Found. Running automatic snatcher.'.format(title))
                    self.snatcher.auto_grab(title, year, imdbid, quality)
                    continue

                if status == u'Finished' and keepsearching is True:
                    logging.info(u'{} status is Finished but Keep Searching is enabled. Checking if Finished date is less than {} days ago.'.format(title, keepsearchingdays))
                    if finisheddateobj + keepsearchingdelta <= today:
                        minscore = movie['finished_score'] + keepsearchingscore
                        logging.info(u'{} finished on {}, checking for a better result (min score {}).'.format(title, finisheddate, minscore))
                        self.snatcher.auto_grab(title, year, imdbid, quality, minscore=minscore)
                        continue
                    else:
                        logging.info(u'{} finished on {} and is not within the Keep Searching window.'.format(title, finisheddate))
                        continue
                else:
                    continue

        logging.info(u'Autosearch complete.')
        return

    def search(self, imdbid, title, year, quality):
        ''' Search indexers for releases
        :param imdbid: str imdb identification number (tt123456)
        :param title: str movie title and year (Movie Title 2016)
        sort: str ASC or DESC, order to sort sizes

        Checks predb value in MOVIES table. If not == u'found', does nothing.

        Gets new search results from newznab providers.
        Pulls existing search results and updates new data with old. This way the
            found_date doesn't change.

        Sends ALL results to scoreresults.score() to be (re-)scored and filtered.

        Checks if guid matches entries in MARKEDRESULTS and
            sets status if found. Default status Available.

        Finally stores results in SEARCHRESULTS

        Returns Bool if movie is found.
        '''

        proxy.Proxy.create()

        results = []

        if core.CONFIG['Downloader']['Sources']['usenetenabled']:
            for i in self.nn.search_all(imdbid):
                results.append(i)
        if core.CONFIG['Downloader']['Sources']['torrentenabled']:
            for i in self.torrent.search_all(imdbid, title, year):
                results.append(i)

        proxy.Proxy.destroy()

        old_results = [dict(r) for r in self.sql.get_search_results(imdbid, quality)]

        for old in old_results:
            if old['type'] == 'import':
                results.append(old)

        # update results with old info if guids match
        for idx, result in enumerate(results):
            for old in old_results:
                if old['guid'] == result['guid']:
                    result.update(old)
                    results[idx] = result

        scored_results = self.score.score(results, imdbid=imdbid)

        # sets result status based off marked results table
        marked_results = self.sql.get_marked_results(imdbid)
        if marked_results:
            for result in scored_results:
                if result['guid'] in marked_results:
                    result['status'] = marked_results[result['guid']]

        if not self.store_results(scored_results, imdbid):
            return False

        if not self.update.movie_status(imdbid):
            logging.info(u'No acceptable results found for {}'.format(imdbid))
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

        logging.info(u'{} results found for {}. Storing results.'.format(len(results), imdbid))

        # This iterates through the new search results and submits only results we haven't already stored. This keeps it from overwriting the FoundDate
        BATCH_DB_STRING = []

        for result in results:
            DB_STRING = result
            DB_STRING['imdbid'] = imdbid
            if 'date_found' not in DB_STRING:
                DB_STRING['date_found'] = datetime.date.today()

            BATCH_DB_STRING.append(DB_STRING)

        self.sql.purge_search_results(imdbid=imdbid)

        if BATCH_DB_STRING:
            if self.sql.write_search_results(BATCH_DB_STRING):
                return True
            else:
                return False
        else:
            return True
