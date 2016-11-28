# Handles searching usenet and torrent suppliers. Writes results to sqldb.
import cherrypy
import newznab, scoreresults, sqldb, snatcher, config
import datetime, json
from core.rss import predb
from core.conversions import Conversions

import logging
logging = logging.getLogger(__name__)

class Searcher():

    def __init__(self):
        self.nn = newznab.NewzNab()
        self.score = scoreresults.ScoreResults()
        self.sql = sqldb.SQL()
        self.predb = predb.PreDB()
        self.snatcher = snatcher.Snatcher()
        self.conf = config.Config()

    # this only runs when scheduled. Only started by the user when changing search settings.
    def auto_search_and_grab(self, mode=''):
        auto_grab = self.conf['Search']['autograb']

        self.predb.check_all()
        logging.info('Running automatic search.')
        movies = self.sql.get_user_movies()
        if not movies:
            return False
        TABLE_NAME = 'MOVIES'

        for movie in movies:
            imdbid = movie['imdbid']
            title = movie['title']
            if movie['predb'] == 'found':
                if mode == 'all':
                    self.search(imdbid, title)
                elif movie['status'] in ['Wanted', 'Found']:
                        self.search(imdbid, title)


        if auto_grab == 'true':
            # In case we found something we'll check this again.
            movies = self.sql.get_user_movies()
            if not movies:
                return False
            for movie in movies:
                if movie['status'] == 'Found':
                    logging.info('Running automatic snatcher for {}.'.format(movie['title']))
                    self.snatcher.auto_grab(movie['imdbid'])

        logging.info('Autosearch complete.')
        return

    # searches indexer for movies. Returns bool if found
    def search(self, imdbid, title):
        TABLE_NAME = 'MOVIES'

        newznab_results = self.nn.search_all(imdbid)
        scored_results = self.score.score(newznab_results, imdbid, 'nzb')
        ## eventually add search for torrents

        # sets result status based off marked results table
        marked_results =  self.sql.get_marked_results(imdbid)
        if marked_results:
            for result in scored_results:
                if result['guid'] in marked_results:
                    result['status'] = marked_results[result['guid']]


        if scored_results:
            if self.store_results(scored_results, imdbid):
                return True
            else:
                return False
        else:
            logging.info('No acceptable results found for {}.'.format(imdbid))
            logging.info('Updating {} {} status to wanted.'.format(TABLE_NAME, imdbid))
            if self.sql.update(TABLE_NAME, 'status', 'Wanted', imdbid=imdbid ):
                return True
            else:
                return False


    def store_results(self, results, imdbid):

        logging.info('{} results found for {}. Storing results.'.format(len(results), imdbid))

        # This iterates through the new search results and submits only results we haven't already stored. This keeps it from overwriting the FoundDate
        kept_guids = []
        BATCH_DB_STRING = []
        existing_results = self.sql.get_search_results(imdbid)

        if existing_results:
            for res in existing_results:
                kept_guids.append(res['guid'])

        for result in results:
            if result['guid'] in kept_guids:
                continue
            else:
                DB_STRING = result
                DB_STRING['imdbid'] = imdbid
                DB_STRING['date_found'] = datetime.date.today()

                BATCH_DB_STRING.append(DB_STRING)

        if BATCH_DB_STRING:
            if self.sql.write_search_results(BATCH_DB_STRING):
                if self.update_movie_status(imdbid):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return True

    # Set MOVIE status to appropriate flag
    def update_movie_status(self, imdbid):

        result_status = self.sql.get_distinct('SEARCHRESULTS', 'status', 'imdbid', imdbid)
        if not result_status:
            return False

        if 'Finished' in result_status:
            status = 'Finished'
        if 'Snatched' in result_status:
            status = 'Snatched'
        elif 'Available' in result_status:
            status = 'Found'
        else:
            status = 'Wanted'

        logging.info('Setting MOVIES {} status to {}.'.format(imdbid, status))
        if self.sql.update('MOVIES', 'status', status, imdbid=imdbid ):
            return True
        else:
            return False

