import os
import PTN
import urllib2
import json
import shutil
import re
from core import config, sqldb, ajax, snatcher

import logging
logging = logging.getLogger(__name__)

class PostProcessing(object):

    def __init__(self):
        self.conf = config.Config()
        self.pp_conf = self.conf['Postprocessing']
        self.sql = sqldb.SQL()

    def failed(self, guid, path):
        if guid == 'None':
            return 'Success'

        ajax.Ajax().mark_bad(guid)

        imdbid = self.sql.get_imdbid_from_guid(guid)
        if imdbid:
            logging.info('Post-processing {} as failed'.format(imdbid))
            try:
                if self.conf['Search']['autograb'] == 'true':
                    s = snatcher.Snatcher()

                    if s.auto_grab(imdbid) == True:
                        # This ulitmately goes to an ajax response, so we can't return a bool
                        return 'Success'
                    else:
                        logging.info('Setting status of {} back to Wanted.'.format(imdbid))
                        if not self.sql.update('MOVIES', 'status', 'Wanted', imdbid=imdbid):
                            return False
                        return 'Success'
                else:
                    return 'Success'
            except Exception, e:
                logging.error('Post-processing failed.', exc_info=True)
                return 'Failed'

    def complete(self, guid, path):
        logging.info('Post-processing {} as complete.'.format(guid))
        imdbid = None

        if guid != 'None':
            imdbid = self.sql.get_imdbid_from_guid(guid)
            if not imdbid:
                imdbid = None
        movie_data = self.movie_data(imdbid, path)

        if self.pp_conf['renamerenabled'] == 'true':
            new_name = self.renamer(movie_data)
            if new_name == False:
                return 'Fail'
            else:
                movie_data['filename'] = new_name

        if self.pp_conf['moverenabled'] == 'true':
            if self.mover(movie_data) == False:
                return 'Fail'
            else:
                if self.pp_conf['cleanupenabled'] == 'true':
                    self.cleanup(movie_data)


        imdbid = movie_data['imdbid']
        try:
            if not self.sql.update('MOVIES', 'status', 'Finished', imdbid=imdbid):
                return False
            if not self.sql.update('SEARCHRESULTS', 'status', 'Finished', guid=guid):
                return False
            if self.sql.row_exists('MARKEDRESULTS', guid=guid) and guid != 'None':
                if not self.sql.update('MARKEDRESULTS', 'status', 'Finished', guid=guid):
                    return False

            imdbid = self.sql.get_imdbid_from_guid(guid)
            DB_STRING = {}
            DB_STRING['imdbid'] = imdbid
            DB_STRING['guid'] = guid
            DB_STRING['status'] = 'Snatched'
            if not self.sql.write('MARKEDRESULTS', DB_STRING):
                return 'Fail'


            logging.info('{} postprocessing finished.'.format(imdbid))
            return 'Success'
        except Exception, e:
            logging.error('Post-processing failed.', exc_info=True)
            return 'Fail'


    def movie_data(self, imdbid, path):
        #this is out base dict. We declare everything here in case we can't find a value later on. We'll still have the key in the dict, so we don't need to check if a key exists every time we want to use one. This MUST match all of the options the user is able to select in Settings.

        data = {
            'title':'',
            'year':'',
            'resolution': '',
            'group':'',
            'audiocodec':'',
            'videocodec':'',
            'rated':'',
            'imdbid':''
        }

        # Find the biggest file in the dir. It should be safe to assume that this is the movie.
        files =  os.listdir(path)
        for file in files:
            s = 0
            abspath = os.path.join(path, file)
            size = os.path.getsize(abspath)
            if size > s:
                moviefile = file

        filename, ext = os.path.splitext(moviefile)

        data['filename'] = filename
        data['ext'] = ext
        data['path'] = os.path.normpath(path)

        # Parse what we can from the filename
        titledata = PTN.parse(filename)
        # this key can sometimes be a list, which is a pain to deal with later. We don't ever need it, so del
        if 'excess' in titledata:
            titledata.pop('excess')
        # Make sure this matches our keys
        if 'codec' in titledata:
            titledata['videocodec'] = titledata.pop('codec')
        if 'audio' in titledata:
            titledata['audiocodec'] = titledata.pop('audio')
        data.update(titledata)

        # if we know the imdbid we'll look it up.
        if imdbid:
            localdata = self.sql.get_movie_details(imdbid)
            if localdata:
                data.update(localdata)

        # If we don't know the imdbid we'll look it up at ombd and add their info to the dict. This can happen if we are post-processing a movie that wasn't snatched by Watcher.
        else:
            title = data['title']
            year = data['year']
            search_string = 'http://www.omdbapi.com/?t={}&y={}&plot=short&r=json'.format(title, year).replace(' ', '+')

            request = urllib2.Request( search_string, headers={'User-Agent' : 'Mozilla/5.0'} )

            try:
                omdbdata = json.load(urllib2.urlopen( request ) )
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e:
                logging.error('Post-processing omdb request.', exc_info=True)

            if omdbdata['Response'] == 'True':
                # make the keys all lower case
                omdbdata_lower = dict((k.lower(), v) for k, v in omdbdata.iteritems())
                data.update(omdbdata_lower)

        # remove any invalid characters
        for k, v in data.iteritems():
            # but we have to keep the path unmodified
            if k != 'path':
                data[k] = re.sub(r'[:"*?<>|]+', "", v)

        return data


    def renamer(self, data):
        renamer_string = self.pp_conf['renamerstring']

        existing_file_path = os.path.join(data['path'], data['filename'] + data['ext'])

        new_file_name =  renamer_string.format(**data)

        new_file_path = os.path.join(data['path'], new_file_name + data['ext'])

        logging.info('Renaming {} to {}'.format(existing_file_path, new_file_path))

        try:
            os.rename(existing_file_path, new_file_path)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error('Post-Processing Renamer.', exc_info=True)
            return False
        # return the new name so the mover knows what our file is
        return new_file_name


    def mover(self, data):
        movie_file = os.path.join(data['path'], data['filename'] + data['ext'])

        mover_path = self.pp_conf['moverpath']

        target_folder = mover_path.format(**data)

        target_folder = os.path.normpath(target_folder)

        logging.info('Moving {} to {}'.format(movie_file, target_folder))

        try:
            if not os.path.exists(target_folder):
                os.mkdir(target_folder)
        except Exception, e:
            logging.error('Post-processing failed. Could not create folder.', exc_info=True)

        try:
            shutil.move(movie_file, target_folder)
        except Exception, e:
            logging.error('Post-processing failed. Could not move file.', exc_info=True)

        return True

    def cleanup(self, data):
        remove_path = data['path']
        logging.info('Clean Up. Removing {}.'.format(remove_path))
        try:
            shutil.rmtree(remove_path)
        except Exception, e:
            logging.error('Post-processing failed. Could not clean up.', exc_info=True)
