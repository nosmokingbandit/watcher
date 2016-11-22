import cherrypy
import json
from templates import movie_info_popup, movie_status_popup, status
import os
import sys
import datetime
import threading
from core import sqldb, poster, config, scoreresults, snatcher, searcher, scheduler
from core.movieinfo import Omdb
from core.downloaders import sabnzbd, nzbget
from core.rss import predb

import logging
logging = logging.getLogger(__name__)

class Ajax(object):

    def __init__(self):
        self.omdb = Omdb()
        self.config = config.Config()
        self.predb = predb.PreDB()
        self.searcher = searcher.Searcher()
        self.sql = sqldb.SQL()
        self.poster = poster.Poster()
        self.snatcher = snatcher.Snatcher()


    def search_omdb(self, search_term):

        results = self.omdb.search(search_term.replace(' ', '+'))

        if type(results) is str:
            logging.info('No Reulst found for {}'.format(search_term))
            return None
        else:
            for i in results:
                if i['Poster'] == 'N/A':
                    i['Poster'] = 'images/missing_poster.jpg'

            return json.dumps(results)


    def movie_info_popup(self, imdbid):
        mip = movie_info_popup.MovieInfoPopup()
        return mip.html(imdbid)


    def movie_status_popup(self, imdbid):

        msp = movie_status_popup.MovieStatusPopup()
        return msp.html(imdbid)

    def add_wanted_movie(self, data):

        def thread_search_grab(data):
            imdbid = data['imdbid']
            title = data['title']
            self.predb.check_one(data)
            if self.config['Search']['searchafteradd'] == 'true':
                self.searcher.search(imdbid, title)
                # if we don't need to wait to grab the movie do it now.
                if self.config['Search']['autograb'] == 'true' and self.config['Search']['waitdays'] == '0':
                    self.snatcher.auto_grab(imdbid)

        TABLE_NAME = 'MOVIES'

        data = json.loads(data)
        imdbid = data['imdbid']
        title = data['title']


        title_year = (title + data['year']).replace(' ', '_')

        if self.sql.row_exists(TABLE_NAME, imdbid=imdbid):
            logging.info('{} already exists as a wanted movie'.format(title_year, imdbid))
            return '{} is already wanted, cannot add.'.format(title_year, imdbid)

        else:
            data['status'] = 'Wanted'
            data['predb'] = 'None'
            DB_STRING = data
            self.sql.write(TABLE_NAME, DB_STRING)

            t2 = threading.Thread(target=self.poster.save_poster, args=(imdbid, data['poster']))
            t2.start()

            t = threading.Thread(target=thread_search_grab, args=(data,))
            t.start()

            return '{} {} added to wanted list.'.format(title, data['year'])


    def save_settings(self, data):
        # this lets us know if the search criteria has changed so we can start a seach again right away
        def change_alert(data):
            new_quality = data['Quality']
            new_filters = data['Filters']

            old_quality = {}
            for i in self.config['Quality']:
                old_quality[i] = (',').join(self.config['Quality'][i])

            for i in new_quality:
                if new_quality[i] != old_quality[i]:
                    return True

            old_filters = {}
            for i in self.config['Filters']:
                old_filters[i] = (',').join(self.config['Filters'][i])

            for i in new_filters:
                if new_filters[i] != old_filters[i]:
                    return True
            return False

        logging.info('Saving settings.')
        data = json.loads(data)

        change_alert = change_alert(data)

        try:
            self.config.write_dict(data)
            if change_alert:
                self.search_all(purge=True)
                return 'change alert'
            else:
                return 'success'

        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.exception('Writing config.')
            return 'failed'

    def remove_movie(self, imdbid):
        t = threading.Thread(target=self.poster.remove_poster, args=(imdbid,))
        t.start()

        self.sql.remove_movie(imdbid)
        return


    def search(self, imdbid, title):
        if self.searcher.search(imdbid, title):
            return 'DONE'
        else:
            return 'Nothing found. \nIf this is inaccurate please file a bug report.'

    def search_all(self, purge=False):

        if purge == True:
            self.sql.purge_search_results()

        t = threading.Thread(target=self.searcher.auto_search_and_grab, kwargs=({'mode':'all'}))
        t.start()

    def manual_download(self, guid):
        data = self.sql.get_single_search_result(guid)
        return self.snatcher.snatch(data)

    def mark_bad(self, guid):

        TABLE_NAME = 'SEARCHRESULTS'
        if self.sql.row_exists(TABLE_NAME, guid=guid):
            logging.info('Setting status of {} to \'Bad\''.format(guid))
            self.sql.update(TABLE_NAME, 'status', 'Bad', guid=guid)

            # Check to see if all results are bad. If so change MOVIE back to Wanted
            imdbid = self.sql.get_imdbid_from_guid(guid)
            statuses = self.sql.get_distinct('SEARCHRESULTS', 'status', 'imdbid', imdbid)

            moviestatus = ''
            print statuses
            if 'Snatched' not in statuses and 'Finished' not in statuses:
                moviestatus = 'Found'

            if all(s == 'Bad' for s in statuses):
                moviestatus = 'Wanted'

            if moviestatus:
                logging.info('Setting {} back to {}.'.format(imdbid, moviestatus))
                self.sql.update('MOVIES', 'status', moviestatus, imdbid= imdbid)

            TABLE_NAME = 'MARKEDRESULTS'
            if self.sql.row_exists(TABLE_NAME, guid=guid):
                self.sql.update(TABLE_NAME, 'status', 'Bad', guid=guid)
            else:
                DB_STRING = {}
                DB_STRING['imdbid'] = imdbid
                DB_STRING['guid'] = guid
                DB_STRING['status'] = 'Bad'
                self.sql.write(TABLE_NAME, DB_STRING)

            return 'Marked {} as Bad.'.format(guid)

        else:
            return None


    def refresh_list(self, list, imdbid=''):
    # re-renders html for lists in /status so it can be updated when something is searched for, marked bad, snatched, etc...
        if list == '#movie_list':
            return status.Status.movie_list()
        if list == '#result_list':
            return movie_status_popup.MovieStatusPopup().result_list(imdbid)


    def test_downloader_connection(self, mode, data):
        data = json.loads(data)

        if mode == 'sabnzbd':
            if sabnzbd.Sabnzbd.test_connection(data) == True:
                return 'Connection successful.'
            else:
                return sabnzbd.Sabnzbd.test_connection(data)
        if mode == 'nzbget':
            if nzbget.Nzbget.test_connection(data) == True:
                return 'Connection successful.'
            else:
                return nzbget.Nzbget.test_connection(data)


    def server_status(self, mode):
        def server_restart():
            cwd = os.getcwd()
            cherrypy.engine.restart()
            os.chdir(cwd) # again, for the daemon

        def server_shutdown():
            cherrypy.engine.stop()
            cherrypy.engine.exit()
            sys.exit(0)

        if mode == 'restart':
            logging.info('Restarting Server...')
            threading.Timer(1, server_restart).start()

        elif mode == 'shutdown':
            logging.info('Shutting Down Server...')
            threading.Timer(1, server_shutdown ).start()

        elif mode == 'online':
            return str(cherrypy.engine.state)

