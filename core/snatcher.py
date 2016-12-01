from core import sqldb, config
from core.downloaders import sabnzbd, nzbget
from datetime import datetime

import logging
logging = logging.getLogger(__name__)

class Snatcher():

    def __init__(self):
        self.sql = sqldb.SQL()
        self.config = config.Config()

    def auto_grab(self, imdbid):
        '''
        Grabs the best scoring result that isn't 'Bad'
        Returns True or False if movie is snatched
        '''

        logging.info('Selecting best result for {}'.format(imdbid))
        search_results = self.sql.get_search_results(imdbid)
        if not search_results:
            logging.info('Unable to automatically grab {}, no results.'.format(imdbid))
            return False

        # Check if we are past the 'waitdays'
        wait_days = int(self.config['Search']['waitdays'])

        earliest_found = min([x['date_found'] for x in search_results])
        date_found = datetime.strptime(earliest_found, '%Y-%m-%d')

        if (datetime.today() - date_found).days < wait_days:
            logging.info('Earliest found result for {} is {}, waiting {} days to grab best result.'.format(imdbid, date_found, wait_days))
            return False

        # Since seach_results comes back in order of score we can go
        # through in order until we find the first Available result
        # and grab it.
        for result in search_results:
            if result['status'] == 'Available':
                self.snatch(result)
                return True

        logging.info('Unable to automatically grab {}, no Available results.'.format(imdbid))
        return False

    def snatch(self, data):
        '''
        Takes single result dict and sends it to the active downloader.
        Returns response from download.
        Marks release and movie as 'Snatched'
        '''

        # Send to active downloaders
        guid = data['guid']
        imdbid = data['imdbid']
        title = data['title']

        sab_conf = self.config['Sabnzbd']
        if sab_conf['sabenabled'] == 'true' and data['type'] == 'nzb':
            logging.info('Sending nzb to Sabnzbd.')
            sab = sabnzbd.Sabnzbd()
            response = sab.add_nzb(data)

            if response['status'] == True:
                # set status to snatched and add downloader id
                if self.update_status_snatched(guid, imdbid):
                    logging.info('Successfully sent {} to Sabnzbd.'.format(title))
                    return 'Successfully sent to Sabnzbd.'
                else:
                    return 'Error marking result as Snatched. Check logs for more information.'
            else:
                logging.error('SABNZBD: {}'.format(response['status']))
                return "SABNZBD: {}".format(response['status'])

        nzbg_conf = self.config['NzbGet']
        if nzbg_conf['nzbgenabled'] == 'true' and data['type'] == 'nzb':
            logging.info('Sending nzb to NzbGet.')
            response = nzbget.Nzbget.add_nzb(data)

            if type(response) == int and response > 0:
                if self.update_status_snatched(guid, imdbid):
                    logging.info('Successfully sent {} to NzbGet.'.format(title))
                    return 'Successfully sent to NzbGet.'
                else:
                    return 'Error marking result as Snatched. Check logs for more information.'
            else:
                logging.error('NZBGET: Error # {}'.format(response))
                return "NZBGET: Error {}.".format(response)

    def update_status_snatched(self, guid, imdbid):
        '''
        Updates MOVIES, SEARCHRESULTS, and MARKEDRESULTS to 'Snatched'
        Returns True or False on success.
        '''

        # set movie status snatched
        logging.info('Setting MOVIES {} status to Snatched.'.format(imdbid))
        if self.sql.row_exists('MOVIES', imdbid=imdbid):
            if not self.sql.update('MOVIES', 'status', 'Snatched', imdbid=imdbid):
                return False
        else:
            logging.error('Attempting to snatch a movie that doesn\'t exist in table MOVIES. I don\'t know how this happened.'.format(imdbid))
            return False

        # set search result to snatched
        logging.info('Setting SEARCHRESULTS {} to Snatched.'.format(guid))
        TABLE_NAME = 'SEARCHRESULTS'
        if self.sql.row_exists(TABLE_NAME, guid=guid):
            if not self.sql.update(TABLE_NAME, 'status', 'Snatched', guid=guid ):
                return False
        else:
            logging.error('Trying to set {} as snatched, but it doesn\'t exist in {}.'.format(guid, TABLE_NAME))

        TABLE_NAME = 'MARKEDRESULTS'
        if self.sql.row_exists(TABLE_NAME, guid=guid):
            if not self.sql.update(TABLE_NAME, 'status', 'Snatched', guid=guid ):
                return False
        else:
            DB_STRING = {}
            DB_STRING['imdbid'] = imdbid
            DB_STRING['guid'] = guid
            DB_STRING['status'] = 'Snatched'
            if self.sql.write(TABLE_NAME, DB_STRING):
                logging.info('Marked {} as Snatched'.format(guid))
                return True
            else:
                return False



