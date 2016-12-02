import cherrypy
import json
from templates import movie_info_popup, movie_status_popup, status
import os
import sys
import datetime
import threading
import core
from core import sqldb, poster, config, scoreresults, snatcher, searcher, scheduler, version
from core.conversions import Conversions
from core.movieinfo import Omdb
from core.downloaders import sabnzbd, nzbget
from core.rss import predb

import logging
logging = logging.getLogger(__name__)

class Ajax(object):
    '''
    These are all the methods that handle ajax post/get requests from the browser.
    '''

    def __init__(self):
        self.omdb = Omdb()
        self.config = config.Config()
        self.predb = predb.PreDB()
        self.searcher = searcher.Searcher()
        self.sql = sqldb.SQL()
        self.poster = poster.Poster()
        self.snatcher = snatcher.Snatcher()

    def search_omdb(self, search_term):
        '''
        Searches OMDB for the user-supplied term.
        Returns a json string of a list of dicts that contain omdb's data.
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
        '''
        Simply calls on the movie_info_popup template to contruct the html for this movie.
        Returns html string.
        '''
        mip = movie_info_popup.MovieInfoPopup()
        return mip.html(imdbid)


    def movie_status_popup(self, imdbid):
        '''
        Simply calls on the movie_status_popup template to contruct the html for this movie.
        Returns html string.
        '''
        msp = movie_status_popup.MovieStatusPopup()
        return msp.html(imdbid)

    def add_wanted_movie(self, data):
        '''
        Adds a movie to the Wanted list. Takes dict 'data' and writes it to MOVIES table.
        Will start an automatic search and snatch if the settings allow.
        Returns a success/fail message.
        '''
        def thread_search_grab(data):
            imdbid = data['imdbid']
            title = data['title']
            self.predb.check_one(data)
            if core.CONFIG['Search']['searchafteradd'] == 'true':
                if self.searcher.search(imdbid, title):
                    # if we don't need to wait to grab the movie do it now.
                    if core.CONFIG['Search']['autograb'] == 'true' and core.CONFIG['Search']['waitdays'] == '0':
                        self.snatcher.auto_grab(imdbid)

        TABLE = 'MOVIES'

        data = json.loads(data)
        imdbid = data['imdbid']
        title = data['title']

        title_year = (title + data['year']).replace(' ', '_')

        if self.sql.row_exists(TABLE, imdbid=imdbid):
            logging.info('{} already exists as a wanted movie'.format(title_year, imdbid))
            return '{} is already wanted, cannot add.'.format(title_year, imdbid)

        else:
            data['status'] = 'Wanted'
            data['predb'] = 'None'
            DB_STRING = data
            if self.sql.write(TABLE, DB_STRING):

                t2 = threading.Thread(target=self.poster.save_poster, args=(imdbid, data['poster']))
                t2.start()

                t = threading.Thread(target=thread_search_grab, args=(data,))
                t.start()

                title = title.replace('_', ' ')
                return '{} {} added to wanted list.'.format(title, data['year'])
            else:
                return 'Could not write to database. Check logs for more information.'


    def save_settings(self, data):
        '''
        Saves *all* of the user's settings.
        Returns 'failed' or 'success'
        Alert messages are handled by the javascript.
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
        '''
        Deletes a movie, its seach results, and poster.
        On error returns 'error', which is then hanlded by the javascript.
        '''
        t = threading.Thread(target=self.poster.remove_poster, args=(imdbid,))
        t.start()

        if self.sql.remove_movie(imdbid):
            return
        else:
            return 'error'

    def search(self, imdbid, title):
        '''
        Searches for a specific movie.
        Returns 'done' when done.
        '''
        self.searcher.search(imdbid, title)
        return 'done'

    def manual_download(self, guid):
        '''
        Sends a search result to the downloader when the user clicks the Download Now button.
        Returns an error message if the sql query fails.
        Returns the success/fail message from Snatcher.snatch()
        '''
        data = self.sql.get_single_search_result(guid)
        if data:
            return self.snatcher.snatch(data)
        else:
            return 'Unable to get download information from the database. Check logs for more information.'

    def mark_bad(self, guid):
        '''
        Marks a specific search result's guid as Bad.
        Returns either a success or failure message.
        '''
        TABLE = 'SEARCHRESULTS'
        logging.info('Marking {} as bad.'.format(guid))

        if self.sql.row_exists(TABLE, guid=guid):
            logging.info('Setting status of {} to \'Bad\''.format(guid))
            if not self.sql.update(TABLE, 'status', 'Bad', guid=guid):
                return 'Could not update {} to Bad. Check logs for more information.'.format(guid)

            # Check to see if all results are bad. If so change MOVIE back to Wanted
            imdbid = self.sql.get_imdbid_from_guid(guid)
            if imdbid:
                statuses = self.sql.get_distinct('SEARCHRESULTS', 'status', 'imdbid', imdbid)
                if not statuses:
                    return 'Could not set Movie status. Check logs for more information.'.format()

            moviestatus = ''
            if 'Snatched' not in statuses and 'Finished' not in statuses:
                moviestatus = 'Found'

            if all(s == 'Bad' for s in statuses):
                moviestatus = 'Wanted'

            if moviestatus:
                logging.info('Setting {} back to {}.'.format(imdbid, moviestatus))
                if not self.sql.update('MOVIES', 'status', moviestatus, imdbid= imdbid):
                    return 'Could not update {} to {}. Check logs for more information.'.format(imdbid, moviestatus)

            TABLE = 'MARKEDRESULTS'
            if self.sql.row_exists(TABLE, guid=guid):
                if not self.sql.update(TABLE, 'status', 'Bad', guid=guid):
                    return 'Could not update {} to Bad. Check logs for more information.'.format(guid)
                else:
                    return 'Successfully marked result as Bad.'.format(guid)

            else:
                DB_STRING = {}
                DB_STRING['imdbid'] = imdbid
                DB_STRING['guid'] = guid
                DB_STRING['status'] = 'Bad'
                if self.sql.write(TABLE, DB_STRING):
                    return 'Successfully marked result as Bad.'.format(guid)
                else:
                    return 'Could not add {} to {}. Check logs for more information.'.format(guid, TABLE)

        else:
            logging.info('Successfully marked {} as Bad.'.format(guid))
            return 'Successfully marked result as Bad.'.format(guid)


    def refresh_list(self, list, imdbid=''):
        '''
        Re-renders html for lists in /status so it can be updated when something is searched for, marked bad, snatched, etc...
        Returns html.
        '''
        if list == '#movie_list':
            return status.Status.movie_list()
        if list == '#result_list':
            return movie_status_popup.MovieStatusPopup().result_list(imdbid)


    def test_downloader_connection(self, mode, data):
        '''
        This simply fires off the staticmethod test_connection for the downloader app and returns a success/failure message.
        '''
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
        '''
        This is a set of methods to test or set the server status.
        The only one that returns a value is 'online' which sends the string ENGINE.started, ENGINE.stopped, etc.
        '''
        def server_restart():
            cwd = os.getcwd()
            cherrypy.engine.restart()
            os.chdir(cwd) # again, for the daemon
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
            threading.Timer(1, server_shutdown ).start()
            return

        elif mode == 'online':
            return str(cherrypy.engine.state)


    def update_now(self, mode):
        '''
        This sets us up to update. The mode='set_true' is sent when the user clicks the Update Now button.
        Then when the update page loads it sends mode='update_now'.
        This way if the user goes to the update page without first setting 'set_true' it will redirect them back to status.
        '''
        if mode == 'set_true':
            core.UPDATING = True
            yield 'true'
        if mode == 'update_now':
            update_status = version.Version().manager.execute_update()
            core.UPDATING = False
            if update_status == False:
                logging.info('Update Failed.')
                yield 'failed'
            elif update_status == True:
                yield 'true'
                logging.info('Respawning process...')
                cherrypy.engine.stop()
                python = sys.executable
                os.execl(python, python, * sys.argv)
        else:
            return

    def update_quality_settings(self, quality, imdbid):
        '''
        This takes the information from /movie_status_popup's quality change dialog and update the database entry. quality is the json database string, and imdbid is the imdbid for the target movie.

        Returns 'same' if there is no change (which the javascript ignores), returns the next automatic search time if the criteria has changed, or a failure message. Javascript constructs the alert message for the user if the results are changed.
        '''

        tabledata = self.sql.get_movie_details(imdbid)

        if tabledata == False:
            return 'Could not get existing information from sql table. Check logs for more information.'
        else:
            tabledata = tabledata['quality']

        # check if we need to purge old results and alert the user.
        if tabledata == quality:
            return 'same'

        else:
            logging.info('Updating quality for {}.'.format(imdbid))
            if not self.sql.update('MOVIES', 'quality', quality, imdbid=imdbid):
                return 'Could not save quality to database. Check logs for more information. '
            else:
                if not self.sql.purge_search_results(imdbid):
                    return 'Search criteria has changed, but old search results could not be purged. Check logs for more information.'
                if not self.sql.update('MOVIES', 'status', 'Wanted', imdbid=imdbid):
                    return 'Search criteria has changed, old search results have been purged, but the movie status could not be set. Check logs for more information.'
                else:
                    return Conversions.human_datetime(core.NEXT_SEARCH)


