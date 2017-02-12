import datetime
import json
import logging
import os
import re
import shutil
import urllib2

import cherrypy
import core
import PTN
from core import plugins, movieinfo, snatcher, sqldb, updatestatus

logging = logging.getLogger(__name__)


class Postprocessing(object):
    exposed = True

    def __init__(self):
        self.tmdb = movieinfo.TMDB()
        self.plugins = plugins.Plugins()
        self.sql = sqldb.SQL()
        self.snatcher = snatcher.Snatcher()
        self.update = updatestatus.Status()

    def null(*args, **kwargs): return

    @cherrypy.expose
    def POST(self, **data):
        ''' Handles post-processing requests.
        :kwparam **dara: keyword params send through POST request URL

        required kw params:
            apikey: str Watcher api key
            mode: str post-processing mode (complete, failed)
            guid: str download link of file. Can be url or magnet link.
            path: str path to downloaded files. Can be single file or dir

        optional kw params:
            imdbid: str imdb identification number (tt123456)
            downloadid: str id number from downloader

        Returns str json.dumps(dict) to post-process reqesting application.
        '''

        logging.info(u'#################################')
        logging.info(u'Post-processing request received.')
        logging.info(u'#################################')

        # check for required keys
        for key in ['apikey', 'mode', 'guid', 'path']:
            if key not in data:
                logging.info(u'Missing key {}'.format(key))
                return json.dumps({'response': 'false',
                                  'error': 'missing key: {}'.format(key)})

        # check if api key is correct
        if data['apikey'] != core.CONFIG['Server']['apikey']:
            logging.info(u'Incorrect API key.'.format(key))
            return json.dumps({'response': 'false',
                              'error': 'incorrect api key'})

        # check if mode is valid
        if data['mode'] not in ['failed', 'complete']:
            logging.info(u'Invalid mode value: {}.'.format(data['mode']))
            return json.dumps({'response': 'false',
                              'error': 'invalid mode value'})

        # modify path based on remote mapping
        data['path'] = self.map_remote(data['path'])

        # get the actual movie file name
        data['filename'] = self.get_filename(data['path'])

        if data['filename']:
            logging.info(u'Parsing release name for information.')
            data.update(self.parse_filename(data))

        # Get possible local data or get TMDB data to merge with self.params.
        logging.info(u'Gathering release information.')
        data.update(self.get_movie_info(data))

        # remove any invalid characters
        for (k, v) in data.iteritems():
            # but we have to keep the path unmodified
            if k != u'path' and type(v) == str:
                data[k] = re.sub(r'[:"*?<>|]+', '', v)

        # At this point we have all of the information we're going to get.
        if data['mode'] == u'failed':
            logging.info(u'Post-processing as Failed.')
            # returns to url:
            response = self.failed(data)
            logging.info(response)
        elif data['mode'] == u'complete':
            logging.info(u'Post-processing as Complete.')

            response = self.complete(data)

            title = response.get('title')
            year = response.get('year')
            imdbid = response.get('imdbid')
            resolution = response.get('resolution')
            rated = response.get('rated')
            original_file = response.get('orig_filename')
            new_file_location = response.get('new_file_location')
            downloadid = response.get('downloadid')
            finished_date = response.get('finished_date')

            self.plugins.finished(title, year, imdbid, resolution, rated, original_file,
                                  new_file_location, downloadid, finished_date)

            logging.info(response)
        else:
            logging.info(u'Invalid mode value: {}.'.format(data['mode']))
            return json.dumps({'response': 'false',
                               'error': 'invalid mode value'}, indent=2, sort_keys=True)

        logging.info(u'#################################')
        logging.info(u'Post-processing complete.')
        logging.info(u'#################################')

        return json.dumps(response, indent=2, sort_keys=True)

    @cherrypy.expose
    def GET(self, **data):
        ''' Handles post-processing requests.
        :kwparam **data: keyword params send through GET request URL

        required kw params:
            apikey: str Watcher api key
            mode: str post-processing mode (complete, failed)
            guid: str download link of file. Can be url or magnet link.
            path: str path to downloaded files. Can be single file or dir

        optional kw params:
            imdbid: str imdb identification number (tt123456)
            downloadid: str id number from downloader

        Returns str json.dumps(dict) to post-process reqesting application.
        '''

        logging.info(u'#################################')
        logging.info(u'Post-processing request received.')
        logging.info(u'#################################')

        # check for required keys
        required_keys = ['apikey', 'mode', 'guid', 'path']

        for key in required_keys:
            if key not in data:
                logging.info(u'Missing key {}'.format(key))
                return json.dumps({'response': 'false',
                                  'error': 'missing key: {}'.format(key)})

        # check if api key is correct
        if data['apikey'] != core.CONFIG['Server']['apikey']:
            logging.info(u'Incorrect API key.'.format(key))
            return json.dumps({'response': 'false',
                              'error': 'incorrect api key'})

        # check if mode is valid
        if data['mode'] not in ['failed', 'complete']:
            logging.info(u'Invalid mode value: {}.'.format(data['mode']))
            return json.dumps({'response': 'false',
                              'error': 'invalid mode value'})

        # get the actual movie file name
        data['filename'] = self.get_filename(data['path'])

        logging.info(u'Parsing release name for information.')
        data.update(self.parse_filename(data))

        # Get possible local data or get TMDB data to merge with self.params.
        logging.info(u'Gathering release information.')
        data.update(self.get_movie_info(data))

        # remove any invalid characters
        for (k, v) in data.iteritems():
            # but we have to keep the path unmodified
            if k != u'path' and type(v) == str:
                data[k] = re.sub(r'[:"*?<>|]+', '', v)

        # At this point we have all of the information we're going to get.
        if data['mode'] == u'failed':
            logging.info(u'Post-processing as Failed.')
            # returns to url:
            response = json.dumps(self.failed(data), indent=2, sort_keys=True)
            logging.info(response)
        elif data['mode'] == u'complete':
            logging.info(u'Post-processing as Complete.')
            # returns to url:
            response = json.dumps(self.complete(data), indent=2, sort_keys=True)
            logging.info(response)
        else:
            logging.info(u'Invalid mode value: {}.'.format(data['mode']))
            return json.dumps({'response': 'false',
                               'error': 'invalid mode value'})

        logging.info(u'#################################')
        logging.info(u'Post-processing complete.')
        logging.info(response)
        logging.info(u'#################################')

        return response

    def get_filename(self, path):
        ''' Looks for the filename of the movie being processed
        :param path: str url-passed path to download dir

        If path is a file, just returns path.
        If path is a directory, finds the largest file in that dir.

        Returns str absolute path /home/user/filename.ext
        '''

        logging.info(u'Finding movie file.')
        if os.path.isfile(path):
            return path
        else:
            # Find the biggest file in the dir. Assume that this is the movie.
            try:
                files = os.listdir(path)
            except Exception, e: # noqa
                logging.error(u'Path not found in filesystem. Will be unable to move or rename.',
                              exc_info=True)
                return ''

            files = []
            for root, dirs, filenames in os.walk(path):
                for file in filenames:
                    files.append(os.path.join(root, file))

            if files == []:
                return ''

            biggestfile = None
            s = 0
            for file in files:
                size = os.path.getsize(file)
                if size > s:
                    biggestfile = file
                    s = size

            logging.info(u'Post-processing file {}.'.format(biggestfile))

            return biggestfile

    def parse_filename(self, data):
        ''' Parses filename for release information
        :param data: dict movie info

        PTN only returns information it finds, so we start with a blank dict
            of keys that we NEED to have, then update it with PTN's data. This
            way when we rename the file it will insert a blank string instead of
            throwing a missing key exception.

        Might eventually replace this with Hachoir-metadata

        Returns dict of parsed data
        '''

        filename = data['filename']
        path = data['path']

        # This is our base dict. Contains all neccesary keys, though they can all be empty if not found.
        metadata = {
            'title': '',
            'year': '',
            'resolution': '',
            'releasegroup': '',
            'audiocodec': '',
            'videocodec': '',
            'source': '',
            'imdbid': ''
            }

        titledata = PTN.parse(os.path.basename(filename))
        # this key is useless
        if 'excess' in titledata:
            titledata.pop('excess')

        if len(titledata) <= 2:
            logging.info(u'Parsing filename doesn\'t look accurate. Parsing parent folder name.')
            path_list = path.split(os.sep)
            titledata = PTN.parse(path_list[-1])
            logging.info(u'Found {} in parent folder.'.format(titledata))
        else:
            logging.info(u'Found {} in filname.'.format(titledata))

        # Make sure this matches our key names
        if 'codec' in titledata:
            titledata['videocodec'] = titledata.pop('codec')
        if 'audio' in titledata:
            titledata['audiocodec'] = titledata.pop('audio')
        if 'quality' in titledata:
            titledata['source'] = titledata.pop('quality')
        if 'group' in titledata:
            titledata['releasegroup'] = titledata.pop('group')
        metadata.update(titledata)

        return metadata

    def get_movie_info(self, data):
        ''' Gets score, imdbid, and other information to help process
        :param data: dict url-passed params with any additional info

        Uses guid to look up local details.
        If that fails, uses downloadid.
        If that fails, searches tmdb for imdbid

        If everything fails returns empty dict {}

        Returns dict of any gathered information
        '''

        config = core.CONFIG['Postprocessing']

        # try to get searchresult using guid first then downloadid
        logging.info(u'Searching local database for guid.')
        result = self.sql.get_single_search_result('guid', data['guid'])
        if not result:
            logging.info('Guid not found.')
            if 'downloadid' in data.keys():
                # try to get result from downloadid
                logging.info(u'Searching local database for downloadid.')
                result = self.sql.get_single_search_result('downloadid', data['downloadid'])
                if result:
                    logging.info(u'Searchresult found by downloadid.')
                    if result['guid'] != data['guid']:
                        logging.info(u'Guid for downloadid does not match local data. '
                                     'Adding guid2 to processing data.')
                        data['guid2'] = result['guid']
        else:
            logging.info(u'Searchresult found by guid.')

        # if we found it, get local movie info
        if result:
            logging.info(u'Searching local database by imdbid.')
            data = self.sql.get_movie_details('imdbid', result['imdbid'])
            if data:
                logging.info(u'Movie data found locally by imdbid.')
                data['finished_score'] = result['score']
            else:
                logging.info(u'Unable to find movie in local db.')

        # Still no luck? Try to get the info from TMDB
        else:
            logging.info(u'Unable to find local data for release. Searching TMDB.')

            search_term = '{} {}'.format(data['title'], data['year'])
            logging.info(u'Searching tmdb for {}'.format(search_term))

            tmdbdata = self.tmdb.search(search_term, single=True)
            data['year'] = tmdbdata['release_date'][:4]
            data['imdbid'] = self.tmdb.get_imdbid(tmdbdata['id'])

        if data:
            # remove unnecessary info
            data.pop('plot', None)
            data.pop('overview', None)

            if not data.get('quality'):
                data['quality'] = 'Default'

            repl = config['replaceillegal']

            for (k, v) in data.iteritems():
                if type(v) == str:
                    data[k] = re.sub(r'[:"*?<>|]+', repl, v)

            return data
        else:
            return {}

    def failed(self, data):
        ''' Post-process failed downloads.
        :param data: dict of gathered data from downloader and localdb/tmdb

        In SEARCHRESULTS marks guid as Bad
        In MARKEDRESULTS:
            Creates or updates entry for guid and optional guid2 with status=Bad
        Updates MOVIES status

        If Clean Up is enabled will delete path and contents.
        If Auto Grab is enabled will grab next best release.

        Returns dict of post-processing results
        '''

        config = core.CONFIG['Postprocessing']

        # dict we will json.dump and send back to downloader
        result = {}
        result['status'] = u'finished'
        result['data'] = data
        result['tasks'] = {}

        # mark guid in both results tables
        logging.info(u'Marking guid as Bad.')
        guid_result = {'url': data['guid']}

        if data['guid']:  # guid can be empty string
            if self.update.searchresults(data['guid'], 'Bad'):
                guid_result['update_SEARCHRESULTS'] = u'true'
            else:
                guid_result['update_SEARCHRESULTS'] = u'false'

            if self.update.markedresults(data['guid'], 'Bad', imdbid=data['imdbid']):
                guid_result['update_MARKEDRESULTS'] = u'true'
            else:
                guid_result['update_MARKEDRESULTS'] = u'false'

        # create result entry for guid
        result['tasks']['guid'] = guid_result

        # if we have a guid2, do it all again
        if 'guid2' in data.keys():
            logging.info(u'Marking guid2 as Bad.')
            guid2_result = {'url': data['guid2']}
            if self.update.searchresults(data['guid2'], 'Bad'):
                guid2_result['update SEARCHRESULTS'] = u'true'
            else:
                guid2_result['update SEARCHRESULTS'] = u'false'

            if self.update.markedresults(data['guid2'], 'Bad', imdbid=data['imdbid'], ):
                guid2_result['update_MARKEDRESULTS'] = u'true'
            else:
                guid2_result['update_MARKEDRESULTS'] = u'false'
            # create result entry for guid2
            result['tasks']['guid2'] = guid2_result

        # set movie status
        if data['imdbid']:
            logging.info(u'Setting MOVIE status.')
            r = str(self.update.movie_status(data['imdbid'])).lower()
        else:
            logging.info(u'Imdbid not supplied or found, unable to update Movie status.')
            r = u'false'
        result['tasks']['update_movie_status'] = r

        # delete failed files
        if config['cleanupfailed']:
            result['tasks']['cleanup'] = {'enabled': 'true', 'path': data['path']}

            logging.info(u'Deleting leftover files from failed download.')
            if self.cleanup(data['path']) is True:
                result['tasks']['cleanup']['response'] = u'true'
            else:
                result['tasks']['cleanup']['response'] = u'false'
        else:
            result['tasks']['cleanup'] = {'enabled': 'false'}

        # grab the next best release
        if core.CONFIG['Search']['autograb']:
            result['tasks']['autograb'] = {'enabled': 'true'}
            if data.get('imdbid') and data.get('quality'):
                if self.snatcher.auto_grab(data['title'], data['year'], data['imdbid'], data['quality']):
                    r = u'true'
                else:
                    r = u'false'
            else:
                r = u'false'
            result['tasks']['autograb']['response'] = r
        else:
            result['tasks']['autograb'] = {'enabled': 'false'}

        # all done!
        result['status'] = u'finished'
        return result

    def complete(self, data):
        '''
        :param data: str guid of downloads
        :param downloadid: str watcher-generated downloadid
        :param path: str path to downloaded files.

        All params can be blank strings ie ""

        In SEARCHRESULTS marks guid as Finished
        In MARKEDRESULTS:
            Creates or updates entry for guid and optional guid with status=bad
        In MOVIES updates finishedscore and finisheddate
        Updates MOVIES status

        Checks to see if we found a movie file. If not, ends here.

        If Renamer is enabled, renames movie file according to core.CONFIG
        If Mover is enabled, moves file to location in core.CONFIG, then...
            If Clean Up enabled, deletes path after Mover finishes.
            Clean Up will not execute without Mover success.

        Returns dict of post-processing results
        '''

        config = core.CONFIG['Postprocessing']

        # dict we will json.dump and send back to downloader
        result = {}
        result['status'] = u'incomplete'
        result['data'] = data
        result['data']['finished_date'] = str(datetime.date.today())
        result['tasks'] = {}

        # mark guid in both results tables
        logging.info(u'Marking guid as Finished.')
        guid_result = {}
        if data['guid']:
            if self.update.searchresults(data['guid'], 'Finished'):
                guid_result['update_SEARCHRESULTS'] = u'true'
            else:
                guid_result['update_SEARCHRESULTS'] = u'false'

            if self.update.markedresults(data['guid'], 'Finished', imdbid=data['imdbid']):
                guid_result['update_MARKEDRESULTS'] = u'true'
            else:
                guid_result['update_MARKEDRESULTS'] = u'false'

            # create result entry for guid
            result['tasks'][data['guid']] = guid_result

        # if we have a guid2, do it all again
        if 'guid2' in data.keys():
            logging.info(u'Marking guid2 as Finished.')
            guid2_result = {}
            if self.update.searchresults(data['guid2'], 'Finished'):
                guid2_result['update_SEARCHRESULTS'] = u'true'
            else:
                guid2_result['update_SEARCHRESULTS'] = u'false'

            if self.update.markedresults(data['guid2'], 'Finished', imdbid=data['imdbid'],
                                         ):
                guid2_result['update_MARKEDRESULTS'] = u'true'
            else:
                guid2_result['update_MARKEDRESULTS'] = u'false'

            # create result entry for guid2
            result['tasks'][data['guid2']] = guid2_result

        # set movie status and add finished date/score
        if data['imdbid']:
            logging.info(u'Setting MOVIE status.')
            r = str(self.update.movie_status(data['imdbid'])).lower()
            self.sql.update('MOVIES', 'finished_date', result['data']['finished_date'],
                            imdbid=data['imdbid'])
            self.sql.update('MOVIES', 'finished_score', result['data'].get('finished_score'),
                            imdbid=data['imdbid'])
        else:
            logging.info(u'Imdbid not supplied or found, unable to update Movie status.')
            r = u'false'
        result['tasks']['update_movie_status'] = r

        # renamer
        if config['renamerenabled']:
            result['tasks']['renamer'] = {'enabled': 'true'}
            result['data']['orig_filename'] = result['data']['filename']
            response = self.renamer(data)
            if response is None:
                result['tasks']['renamer']['response'] = u'false'
            else:
                path = os.path.split(data['filename'])[0]
                data['filename'] = os.path.join(path, response)
                result['tasks']['renamer']['response'] = u'true'
        else:
            logging.info(u'Renamer disabled.')
            result['tasks']['mover'] = {'enabled': 'false'}

        # mover
        if config['moverenabled']:
            result['tasks']['mover'] = {'enabled': 'true'}
            response = self.mover(data)
            if response is False:
                result['tasks']['mover']['response'] = u'false'
            else:
                data['new_file_location'] = response
                result['tasks']['mover']['response'] = u'true'
        else:
            logging.info(u'Mover disabled.')
            result['tasks']['mover'] = {'enabled': 'false'}

        # Delete leftover dir. Skip if createhardlinks enabled or if mover disabled/failed
        if config['cleanupenabled']:
            result['tasks']['cleanup'] = {'enabled': 'true'}

            if config['createhardlink']:
                logging.info('Hardlink creation enabled. Skipping Cleanup.')
                result['tasks']['cleanup']['response'] = 'skipped'
                return result

            # fail if mover disabled or failed
            if config['moverenabled'] is False or \
                    result['tasks']['mover']['response'] == u'false':
                logging.info('Mover either disabled or failed. Skipping Cleanup.')
                result['tasks']['cleanup']['response'] = u'false'
            else:
                if self.cleanup(data['path']):
                    r = u'true'
                else:
                    r = u'false'
                result['tasks']['cleanup']['response'] = r
        else:
            result['tasks']['cleanup'] = {'enabled': 'false'}

        # all done!
        result['status'] = u'finished'
        return result

    def map_remote(self, path):
        ''' Alters directory based on remote mappings settings
        path: str path from download client

        Replaces the base of the file tree with the 'local' mapping.
            Ie, '/home/user/downloads/Watcher' becomes '//server/downloads/Watcher'

        'path' can be file or directory, it doesn't matter.

        If more than one match is found, defaults to the longest path.
            remote: local = '/home/users/downloads/': '//server/downloads/'
                            '/home/users/downloads/Watcher/': '//server/downloads/Watcher/'
            In this case, a supplied remote '/home/users/downloads/Watcher/' will match a
            startswith() for both supplied settings. So we will default to the longest path.
        Returns str new path
        '''

        maps = core.CONFIG['Postprocessing']['RemoteMapping']

        matches = []

        for remote in maps.keys():
            if path.startswith(remote):
                matches.append(remote)
        if not matches:
            return path
        else:
            match = max(matches, key=len)
            new_path = path.replace(match, maps[match])
            logging.info('Changing remote path from {} to {}'.format(path, new_path))
            return new_path

    def compile_path(self, string, data):
        ''' Compiles string to file/path names
        :param string: str brace-formatted string to substitue values
        :data data: dict of values to sub into string

        Takes a renamer/mover path and adds values.
            ie '{title} {year} {resolution}' -> 'Movie 2017 1080P'
        Subs double spaces. Trims trailing spaces. Removes any invalid characters.

        Can return blank string ''

        Sends string to self.sanitize() to remove illegal characters

        Returns str new path
        '''

        for k, v in data.iteritems():
            k = "{"+k+"}"
            if k in string:
                string = string.replace(k, v)

        while '  ' in string:
            string = string.replace('  ', ' ')

        while len(string) > 1 and string[-1] == u' ':
            string = string[:-1]

        string = self.map_remote(string)

        return self.sanitize(string)

    def renamer(self, data):
        ''' Renames movie file based on renamerstring.
        :param data: dict of movie information.

        Renames movie file based on params in core.CONFIG

        Returns str new file name or None on failure
        '''

        config = core.CONFIG['Postprocessing']

        renamer_string = config['renamerstring']

        # check to see if we have a valid renamerstring
        if re.match(r'{(.*?)}', renamer_string) is None:
            logging.info(u'Invalid renamer string {}'.format(renamer_string))
            return None

        # existing absolute path
        abs_path_old = data['filename']
        file_path = os.path.split(data['filename'])[0]

        # get the extension
        ext = os.path.splitext(abs_path_old)[1]

        # get the new file name
        new_name = self.compile_path(renamer_string, data)

        if not new_name:
            logging.info(u'New file name would be blank. Cancelling renamer.')
            return None

        if core.CONFIG['Postprocessing']['replacespaces']:
            new_name = new_name.replace(' ', '.')
        new_name = new_name + ext

        # new absolute path
        abs_path_new = os.path.join(file_path, new_name)

        logging.info(u'Renaming {} to {}'.format(os.path.basename(data['filename']), new_name))
        try:
            os.rename(abs_path_old, abs_path_new)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Renamer failed: Could not rename file.', exc_info=True)
            return None

        # return the new name so the mover knows what our file is
        return new_name

    def mover(self, data):
        '''Moves movie file to path constructed by moverstring
        :param data: dict of movie information.

        Moves file to location specified in core.CONFIG

        Copies and renames additional files

        Returns str new file location or False on failure
        '''

        config = core.CONFIG['Postprocessing']

        # get target dir, remove illegal chars, and normalize
        mover_path = config['moverpath']

        target_folder = os.path.normpath(self.compile_path(mover_path, data))
        target_folder = os.path.join(target_folder, '')
        # if the new folder doesn't exist, make it
        try:
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
        except Exception, e:
            logging.error(u'Mover failed: Could not create missing directory {}.'.format(target_folder), exc_info=True)
            return False

        # Move Movie
        logging.info(u'Moving {} to {}'.format(data['filename'], target_folder))
        try:
            shutil.copystat = self.null
            shutil.move(data['filename'], target_folder)
        except Exception, e: # noqa
            logging.error(u'Mover failed: Could not move file.', exc_info=True)
            return False

        new_file_location = os.path.join(target_folder, os.path.basename(data['filename']))

        # Create hardlink

        if config['createhardlink']:
            logging.info('Creating hardlink from {} to {}.'.format(new_file_location, data['orig_filename']))
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.CreateHardLinkA(data['orig_filename'], new_file_location, 0)
            else:
                os.link(new_file_location, data['orig_filename'])

        logging.info(u'Copying and renaming any extra files.')

        moveextensions = config['moveextensions']
        keep_extentions = [i for i in moveextensions.split(u',') if i != u'']

        renamer_string = config['renamerstring']
        new_name = self.compile_path(renamer_string, data)

        for root, dirs, filenames in os.walk(data['path']):
            for name in filenames:
                old_abs_path = os.path.join(root, name)
                ext = os.path.splitext(old_abs_path)[1]  # '.ext'

                target_file = u'{}{}'.format(os.path.join(target_folder, new_name), ext)

                if ext.replace('.', '') in keep_extentions:
                    append = 0
                    while os.path.isfile(target_file):
                        append += 1
                        new_filename = u'{}({})'.format(new_name, str(append))
                        target_file = u'{}{}'.format(os.path.join(target_folder, new_filename), ext)
                    try:
                        logging.info(u'Moving {} to {}'.format(old_abs_path, target_file))
                        shutil.copyfile(old_abs_path, target_file)
                    except Exception, e: # noqa
                        logging.error(u'Mover failed: Could not copy {}.'.format(old_abs_path), exc_info=True)

        return new_file_location

    def cleanup(self, path):
        ''' Deletes specified path
        :param path: str of path to remover

        path can be file or dir

        Returns Bool on success/failure
        '''

        # if its a dir
        if os.path.isdir(path):
            try:
                shutil.rmtree(path)
                return True
            except Exception, e:
                logging.error(u'Could not delete path.', exc_info=True)
                return False
        elif os.path.isfile(path):
            # if its a file
            try:
                os.remove(path)
                return True
            except Exception, e: # noqa
                logging.error(u'Could not delete path.', exc_info=True)
                return False
        else:
            # if it is somehow neither
            return False

    def sanitize(self, string):
        config = core.CONFIG['Postprocessing']
        repl = config['replaceillegal']

        string = re.sub(r'["*?<>|]+', repl, string)

        drive, path = os.path.splitdrive(string)
        path = path.replace(':', repl)
        return ''.join([drive, path])
