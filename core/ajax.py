import json
import logging
import os
import sys
import threading

import cherrypy
import core
from core import (config, poster, searcher, snatcher, sqldb, updatestatus,
                  version)
from core.conversions import Conversions
from core.downloaders import nzbget, sabnzbd
from core.movieinfo import Omdb
from core.rss import predb
from templates import movie_info_popup, movie_status_popup, status

logging = logging.getLogger(__name__)


class Ajax(object):
    ''' These are all the methods that handle
        ajax post/get requests from the browser.

    Except in special circumstances, all should return a string
        since that is the only datatype sent over http

    '''

    def __init__(self):
        self.omdb = Omdb()
        self.config = config.Config()
        self.predb = predb.PreDB()
        self.searcher = searcher.Searcher()
        self.sql = sqldb.SQL()
        self.poster = poster.Poster()
        self.snatcher = snatcher.Snatcher()
        self.update = updatestatus.Status()

    def search_omdb(self, search_term):
        ''' Search omdb for movies
        :param search_term: str title and year of movie (Movie Title 2016)

        Returns str json-encoded list of dicts that contain omdb's data.
        '''
        results = self.omdb.search(search_term.replace(' ', '+'))

        if type(results) is str:
            logging.info('No Results found for {}'.format(search_term))
            return None
        else:
            for i in results:
                if i['Poster'] == 'N/A':
                    i['Poster'] = 'images/missing_poster.jpg'

            return json.dumps(results)

    def movie_info_popup(self, imdbid):
        ''' Calls movie_info_popup to render html
        :param imdbid: str imdb identification number (tt123456)

        Returns str html content.
        '''

        mip = movie_info_popup.MovieInfoPopup()
        return mip.html(imdbid)

    def movie_status_popup(self, imdbid):
        ''' Calls movie_status_popup to render html
        :param imdbid: str imdb identification number (tt123456)

        Returns str html content.
        '''

        msp = movie_status_popup.MovieStatusPopup()
        return msp.html(imdbid)

    def add_wanted_movie(self, data):
        ''' Adds movie to Wanted list.
        :param data: str json.dumps(dict) of info to add to database.

        Writes data to MOVIES table.
        If Search on Add enabled,
            searches for movie immediately in separate thread.
            If Auto Grab enabled, will snatch movie if found.

        Returns str json.dumps(dict) of status and message
        '''

        data = json.loads(data)

        response = {}

        def thread_search_grab(data):
            imdbid = data['imdbid']
            title = data['title']
            self.predb.check_one(data)
            if core.CONFIG['Search']['searchafteradd'] == 'true':
                if self.searcher.search(imdbid, title):
                    # if we don't need to wait to grab the movie do it now.
                    if core.CONFIG['Search']['autograb'] == 'true' and \
                            core.CONFIG['Search']['waitdays'] == '0':
                        self.snatcher.auto_grab(imdbid)

        TABLE = 'MOVIES'

        imdbid = data['imdbid']
        title = data['title'].replace('_', ' ')
        year = data['year']

        if self.sql.row_exists(TABLE, imdbid=imdbid):
            logging.info('{} {} already exists as a wanted movie'
                .format(title, year, imdbid))

            response['status'] = 'failed'
            response['message'] = '{} {} is already wanted, cannot add.' \
                .format(title, year, imdbid)
            return json.dumps(response)

        else:
            data['status'] = 'Wanted'
            data['predb'] = 'None'
            poster_url = data['poster']
            data['poster'] = 'images/poster/{}.jpg'.format(imdbid)

            DB_STRING = data
            if self.sql.write(TABLE, DB_STRING):

                t2 = threading.Thread(target=self.poster.save_poster,
                    args=(imdbid, poster_url))
                t2.start()

                t = threading.Thread(target=thread_search_grab, args=(data,))
                t.start()

                response['status'] = 'success'
                response['message'] = '{} {} added to wanted list.' \
                    .format(title, year)
                return json.dumps(response)
            else:
                response['status'] = 'failed'
                response['message'] = 'Could not write to database. ' \
                    'Check logs for more information.'
                return json.dumps(response)

    def quick_add(self, imdbid):
        ''' Method to quckly add movie with just imdbid
        :param imdbid: str imdb identification number (tt123456)

        Submits movie with base quality options
        Gets info from omdb and sends to self.add_wanted_movie

        Returns dict of success/fail with message.

        Returns str json.dumps(dict)
        '''

        response = {}

        movie_info = self.omdb.movie_info(imdbid)

        if not movie_info:
            response['status'] = 'failed'
            response['message'] = '{} not found on omdb.'.format(imdbid)
            return response

        quality = {}
        quality['Quality'] = core.CONFIG['Quality']
        quality['Filters'] = core.CONFIG['Filters']

        movie_info['quality'] = json.dumps(quality)

        return self.add_wanted_movie(json.dumps(movie_info))

    def save_settings(self, data):
        ''' Saves settings to config file
        :param data: dict of Section with nested dict of keys and values:
        {'Section': {'key': 'val', 'key2': 'val2'}, 'Section2': {'key': 'val'}}

        Returns str 'failed' or 'success'
        '''

        logging.info('Saving settings.')
        data = json.loads(data)

        try:
            self.config.write_dict(data)
            return 'success'
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.exception('Writing config.')
            return 'failed'

    def remove_movie(self, imdbid):
        ''' Removes movie
        :param imdbid: str imdb identification number (tt123456)

        Removes row from MOVIES, removes any entries in SEARCHRESULTS
        In separate thread deletes poster image.

        Returns srt 'error' or nothing on success
        '''

        t = threading.Thread(target=self.poster.remove_poster, args=(imdbid,))
        t.start()

        if self.sql.remove_movie(imdbid):
            response = {'status': 'success'}
        else:
            response = {'status': 'failed'}
        return json.dumps(response)

    def search(self, imdbid, title):
        ''' Search indexers for specific movie.
        :param imdbid: str imdb identification number (tt123456)
        :param title: str movie title and year

        Returns str 'done' when done.
        '''

        self.searcher.search(imdbid, title)
        return 'done'

    def manual_download(self, guid):
        ''' Sends search result to downloader manually
        :param guid: str download link for nzb/magnet/torrent file.

        Returns str success/fail message
        '''

        data = self.sql.get_single_search_result('guid', guid)
        if data:
            return self.snatcher.snatch(data)
        else:
            return 'Unable to get download information from the database. ' \
                'Check logs for more information.'

    def mark_bad(self, guid, imdbid):
        ''' Marks guid as bad in SEARCHRESULTS and MARKEDRESULTS
        :param guid: srt guid to mark

        Returns success/failure message from update.mark_bad()
        '''

        return self.update.mark_bad(guid, imdbid=imdbid)

    def notification_remove(self, index):
        ''' Removes notification from core.notification
        :param index: int index of notification to remove

        Replaces list item with None as to not affect other indexes.
        When adding new notifs through core.notification, any None values
            will be overwritten before appending to the end of the list.

        Does not return
        '''

        core.NOTIFICATIONS[index] = None

        if core.NOTIFICATIONS[-1] is None:
            core.NOTIFICATIONS.pop()
        return

    def update_check(self):
        ''' Manually check for updates

        Returns str json.dumps(dict) from Version manager update_check()
        '''

        response = version.Version().manager.update_check()
        return json.dumps(response)

    def refresh_list(self, list, imdbid=''):
        ''' Re-renders html for Movies/Results list
        :param list: str the html list id to be re-rendered
        :param imdbid: str imdb identification number (tt123456) <optional>

        Calls template file to re-render a list when modified in the database.
        #result_list requires imdbid.

        Returns str html content.
        '''

        if list == '#movie_list':
            return status.Status.movie_list()
        if list == '#result_list':
            return movie_status_popup.MovieStatusPopup().result_list(imdbid)

    def test_downloader_connection(self, mode, data):
        ''' Test connection to downloader.
        :param mode: str which downloader to test.
        :param data: dict connection information (url, port, login, etc)

        Executes staticmethod in the chosen downloader's class.

        Returns str json.dumps dict:
        {'status': 'false', 'message': 'this is a message'}
        '''

        response = {}

        data = json.loads(data)

        if mode == 'sabnzbd':
            test = sabnzbd.Sabnzbd.test_connection(data)
            if test == True:
                response['status'] = 'true'
                response['message'] = 'Connection successful.'
            else:
                response['status'] = 'false'
                response['message'] = test
        if mode == 'nzbget':
            test = nzbget.Nzbget.test_connection(data)
            if test == True:
                response['status'] = 'true'
                response['message'] = 'Connection successful.'
            else:
                response['status'] = 'false'
                response['message'] = test

        return json.dumps(response)

    def server_status(self, mode):
        ''' Check or modify status of CherryPy server_status
        :param mode: str command or request of state

        Restarts or Shuts Down server in separate thread.
            Delays by one second to allow browser to redirect.

        If mode == 'online', asks server for status.
            (ENGINE.started, ENGINE.stopped, etc.)

        Returns nothing for mode == restart || shutdown
        Returns str server state if mode == online
        '''

        def server_restart():
            cwd = os.getcwd()
            cherrypy.engine.restart()
            os.chdir(cwd)  # again, for the daemon
            return

        def server_shutdown():
            cherrypy.engine.stop()
            cherrypy.engine.exit()
            sys.exit(0)

        if mode == 'restart':
            logging.info('Restarting Server...')
            threading.Timer(1, server_restart).start()
            return

        elif mode == 'shutdown':
            logging.info('Shutting Down Server...')
            threading.Timer(1, server_shutdown).start()
            return

        elif mode == 'online':
            return str(cherrypy.engine.state)

    def update_now(self, mode):
        ''' Starts and executes update process.
        :param mode: str 'set_true' or 'update_now'

        If mode == set_true, sets core.UPDATING to True
        This is done so if the user visits /update without setting true
            they will be redirected back to status.
        Yields 'true' back to browser

        If mode == 'update_now', starts update process.
        Yields 'true' or 'failed'. If true, restarts server.
        '''

        if mode == 'set_true':
            core.UPDATING = True
            yield 'success'  # can be return?
        if mode == 'update_now':
            update_status = version.Version().manager.execute_update()
            core.UPDATING = False
            if update_status is False:
                logging.info('Update Failed.')
                yield 'failed'
            elif update_status is True:
                yield 'success'
                logging.info('Respawning process...')
                cherrypy.engine.stop()
                python = sys.executable
                os.execl(python, python, * sys.argv)
        else:
            return

    def update_quality_settings(self, quality, imdbid):
        ''' Updates quality settings for individual title
        :param quality: str json-formatted dict of quality
                        settings as described below.
        :param imdbid: str imdb identification number (tt123456).

        Takes entered information from /movie_status_popup and
            updates database table if it has changed.

        quality must be formatted as:
            json.dumps({'Quality': {'key': 'val'}, 'Filters': {'key': 'val'}})

        Returns str 'same', error message, or change alert message.
        '''

        tabledata = self.sql.get_movie_details('imdbid', imdbid)

        if tabledata is False:
            return 'Could not get existing information from sql table. ' \
                'Check logs for more information.'
        else:
            tabledata = tabledata['quality']

        # check if we need to purge old results and alert the user.
        if tabledata == quality:
            return 'same'

        else:
            logging.info('Updating quality for {}.'.format(imdbid))
            if not self.sql.update('MOVIES', 'quality', quality, imdbid=imdbid):
                return 'Could not save quality to database. ' \
                    'Check logs for more information.'
            else:
                if not self.sql.purge_search_results(imdbid):
                    return 'Search criteria has changed, but old search results ' \
                        'could not be purged. Check logs for more information.'
                if not self.sql.update('MOVIES', 'status', 'Wanted', imdbid=imdbid):
                    return 'Search criteria has changed, old search results ' \
                        'have been purged, but the movie status could not be set. Check logs for more information.'
                else:
                    return Conversions.human_datetime(core.NEXT_SEARCH)
