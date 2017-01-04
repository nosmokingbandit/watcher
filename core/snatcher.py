import logging
from datetime import datetime

import core
from core import sqldb, updatestatus
from core.downloaders import nzbget, sabnzbd

logging = logging.getLogger(__name__)


class Snatcher():

    def __init__(self):
        self.sql = sqldb.SQL()
        self.update = updatestatus.Status()
        return

    def auto_grab(self, imdbid, minscore=0):
        ''' Grabs the best scoring result that isn't 'Bad'

        This simply picks the best release, actual snatching is
            handled by self.snatch()

        Returns True or False if movie is snatched
        '''

        logging.info('Selecting best result for {}'.format(imdbid))
        search_results = self.sql.get_search_results(imdbid)
        if not search_results:
            logging.info('Unable to automatically grab {}, no results.'.format(imdbid))
            return False

        # Check if we are past the 'waitdays'
        wait_days = int(core.CONFIG['Search']['waitdays'])

        earliest_found = min([x['date_found'] for x in search_results])
        date_found = datetime.strptime(earliest_found, '%Y-%m-%d')

        if (datetime.today() - date_found).days < wait_days:
            logging.info('Earliest found result for {} is {}, waiting {} days to grab best result.'.format(imdbid, date_found, wait_days))
            return False

        # Since seach_results comes back in order of score we can go
        # through in order until we find the first Available result
        # and grab it.
        for result in search_results:
            status = result['status']

            if result['status'] == 'Available' and result['score'] > minscore:
                self.snatch(result)
                return True
            # if doing a re-search, if top ranked result is Snatched we have nothing to do.
            if status in ['Snatched', 'Finished']:
                logging.info('Top-scoring release for {} has already been snatched.'.format(imdbid))
                return False

        logging.info('Unable to automatically grab {}, no Available results.'.format(imdbid))
        return False

    def snatch(self, data):
        '''
        Takes single result dict and sends it to the active downloader.
        Returns response from download.
        Marks release and movie as 'Snatched'

        Returns dict {'response': 'true', 'message': 'lorem impsum'}
        '''

        data = dict(data)

        # Send to active downloaders
        guid = data['guid']
        imdbid = data['imdbid']
        title = data['title']
        data['title'] = u'{}.Watcher'.format(data['title'])

        # If sending to SAB
        sab_conf = core.CONFIG['Sabnzbd']
        if sab_conf['sabenabled'] == 'true' and data['type'] == 'nzb':
            logging.info('Sending nzb to Sabnzbd.')
            response = sabnzbd.Sabnzbd.add_nzb(data)

            if response['response'] is 'true':

                # store downloadid in database
                self.sql.update('SEARCHRESULTS', 'downloadid', response['downloadid'], guid=guid)

                if self.update_status_snatched(guid, imdbid):
                    logging.info(u'Successfully sent {} to Sabnzbd.'.format(title))
                    return {'response': 'true', 'message': 'Sent to Sabnzbd.'}
                else:
                    return {'response': 'false', 'error': 'Could not mark '
                            'search result as Snatched.'}
            else:
                return response

        # If sending to NZBGET
        nzbg_conf = core.CONFIG['NzbGet']
        if nzbg_conf['nzbgenabled'] == 'true' and data['type'] == 'nzb':
            logging.info('Sending nzb to NzbGet.')
            response = nzbget.Nzbget.add_nzb(data)

            if response['response'] is 'true':

                # store downloadid in database
                self.sql.update('SEARCHRESULTS', 'downloadid', response['downloadid'], guid=guid)

                if self.update_status_snatched(guid, imdbid):
                    logging.info(u'Successfully sent {} to NZBGet.'.format(title))
                    return {'response': 'true', 'message': 'Sent to NZBGet.'}
                else:
                    return {'response': 'false', 'error': 'Could not mark '
                            'search result as Snatched.'}
            else:
                return response

    def update_status_snatched(self, guid, imdbid):
        '''
        Updates MOVIES, SEARCHRESULTS, and MARKEDRESULTS to 'Snatched'
        Returns Bool on success/fail
        '''

        if not self.update.searchresults(guid, 'Snatched'):
            return False

        if not self.update.markedresults(guid, 'Snatched', imdbid=imdbid):
            return False

        if not self.update.movie_status(imdbid):
            return False

        return True
