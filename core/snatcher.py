import logging
from datetime import datetime
import urllib2
import core
from core import plugins, sqldb, updatestatus
from core.downloaders import deluge, qbittorrent, nzbget, sabnzbd, transmission, rtorrent

logging = logging.getLogger(__name__)


class Snatcher():
    ''' Clarification notes:

    When snatching a torrent, the downloadid should *always* be the torrent hash.
    When snatching NZBs use the client-supplied download id if possible. If the client
        does not return a download-id, use None.

    '''

    def __init__(self):
        self.plugins = plugins.Plugins()
        self.sql = sqldb.SQL()
        self.update = updatestatus.Status()
        return

    def auto_grab(self, movie, minscore=0):
        ''' Grabs the best scoring result that isn't 'Bad'
        title: str title of movie
        year: str year of movie release
        imdbid: str imdb id #
        quality: str name of quality profile, used to determine sort order

        This simply picks the best release, actual snatching is
            handled by self.snatch()

        Returns True or False if movie is snatched
        '''

        try:
            imdbid = movie['imdbid']
            quality = movie['quality']
            year = movie['year']
        except Exception, e: #noqa
            logging.error('Invalid movie data.', exc_info=True)

        search_results = self.sql.get_search_results(imdbid, quality)
        if not search_results:
            logging.warning(u'Unable to automatically grab {}, no results.'.format(imdbid))
            return False

        # Filter out any results we don't want to grab
        search_results = [i for i in search_results if i['type'] != 'import']
        if not core.CONFIG['Downloader']['Sources']['usenetenabled']:
            search_results = [i for i in search_results if i['type'] != 'nzb']
        if not core.CONFIG['Downloader']['Sources']['torrentenabled']:
            search_results = [i for i in search_results if i['type'] not in ['torrent', 'magnet']]

        if not search_results:
            logging.warning(u'Unable to automatically grab {}, no results for enabled downloader.'.format(imdbid))
            return False

        # Check if we are past the 'waitdays'
        wait_days = core.CONFIG['Search']['waitdays']

        earliest_found = min([x['date_found'] for x in search_results])
        date_found = datetime.strptime(earliest_found, '%Y-%m-%d')

        if (datetime.today() - date_found).days < wait_days:
            logging.info(u'Earliest found result for {} is {}, waiting {} days to grab best result.'.format(imdbid, date_found, wait_days))
            return False

        # Since seach_results comes back in order of score we can go
        # through in order until we find the first Available result
        # and grab it.
        logging.info(u'Selecting best result for {}'.format(imdbid))
        for result in search_results:
            result = dict(result)
            status = result['status']
            result['year'] = year

            if result['status'] == u'Available' and result['score'] > minscore:
                self.snatch(result)
                return True
            # if doing a re-search, if top ranked result is Snatched we have nothing to do.
            if status in ['Snatched', 'Finished']:
                logging.info(u'Top-scoring release for {} has already been snatched.'.format(imdbid))
                return False

        logging.warning(u'Unable to automatically grab {}, no Available results.'.format(imdbid))
        return False

    def snatch(self, data):
        '''
        Takes single result dict and sends it to the active downloader.
        Returns response from download.
        Marks release and movie as 'Snatched'

        Returns dict {u'response': True, 'message': 'lorem impsum'}
        '''

        if data['type'] == 'import':
            return {u'response': False, u'error': u'Cannot download imports.'}

        imdbid = data['imdbid']
        resolution = data['resolution']
        kind = data['type']
        info_link = urllib2.quote(data['info_link'], safe='')
        indexer = data['indexer']
        title = data['title']
        year = data['year']

        if data['type'] == 'nzb':
            if core.CONFIG['Downloader']['Sources']['usenetenabled']:
                response = self.snatch_nzb(data)
            else:
                return {u'response': False, u'message': u'NZB submitted but nzb snatching is disabled.'}

        if data['type'] in ['torrent', 'magnet']:
            if core.CONFIG['Downloader']['Sources']['torrentenabled']:
                response = self.snatch_torrent(data)
            else:
                return {u'response': False, u'message': u'Torrent submitted but torrent snatching is disabled.'}

        if response['response'] is True:
            downloader = response['downloader']
            downloadid = response['downloadid']

            self.plugins.snatched(title, year, imdbid, resolution, kind, downloader, downloadid, indexer, info_link)
            return response
        else:
            return response

    def snatch_nzb(self, data):
        guid = data['guid']
        imdbid = data['imdbid']
        title = data['title']

        # If sending to SAB
        sab_conf = core.CONFIG['Downloader']['Usenet']['Sabnzbd']
        if sab_conf['enabled'] is True:
            logging.info(u'Sending nzb to Sabnzbd.')
            response = sabnzbd.Sabnzbd.add_nzb(data)

            if response['response'] is True:

                # store downloadid in database
                self.sql.update('SEARCHRESULTS', 'downloadid', response['downloadid'], guid=guid)

                if self.update_status_snatched(guid, imdbid):
                    logging.info(u'Successfully sent {} to Sabnzbd.'.format(title))
                    return {u'response': True, u'message': u'Sent to SABnzbd.', u'downloader': u'SABnzb', u'downloadid': response['downloadid']}
                else:
                    return {u'response': False, u'error': u'Could not mark '
                            'search result as Snatched.'}
            else:
                return response

        # If sending to NZBGET
        nzbg_conf = core.CONFIG['Downloader']['Usenet']['NzbGet']
        if nzbg_conf['enabled'] is True:
            logging.info(u'Sending nzb to NzbGet.')
            response = nzbget.Nzbget.add_nzb(data)

            if response['response'] is True:

                # store downloadid in database
                self.sql.update('SEARCHRESULTS', 'downloadid', response['downloadid'], guid=guid)

                if self.update_status_snatched(guid, imdbid):
                    logging.info(u'Successfully sent {} to NZBGet.'.format(title))
                    return {u'response': True, u'message': u'Sent to NZBGet.', u'downloader': u'NZBGet', u'downloadid': response['downloadid']}
                else:
                    return {u'response': False, u'error': u'Could not mark '
                            'search result as Snatched.'}
            else:
                return response

    def snatch_torrent(self, data):
        guid = data['guid']
        imdbid = data['imdbid']
        title = data['title']
        kind = data['type']

        # If sending to Transmission
        transmission_conf = core.CONFIG['Downloader']['Torrent']['Transmission']
        if transmission_conf['enabled'] is True:
            logging.info(u'Sending {} to Transmission.'.format(kind))
            response = transmission.Transmission.add_torrent(data)

            if response['response'] is True:

                # store downloadid in database
                self.sql.update('SEARCHRESULTS', 'downloadid', response['downloadid'], guid=guid)

                if self.update_status_snatched(guid, imdbid):
                    logging.info(u'Successfully sent {} to NZBGet.'.format(title))
                    return {u'response': True, u'message': u'Sent to Tranmission.', u'downloader': u'Transmission', u'downloadid': response['downloadid']}
                else:
                    return {u'response': False, u'error': u'Could not mark '
                            'search result as Snatched.'}
            else:
                return response

        # If sending to QBittorrent
        qbit_conf = core.CONFIG['Downloader']['Torrent']['QBittorrent']
        if qbit_conf['enabled'] is True:
            logging.info(u'Sending {} to QBittorrent.'.format(kind))
            response = qbittorrent.QBittorrent.add_torrent(data)

            if response['response'] is True:

                # store downloadid in database
                self.sql.update('SEARCHRESULTS', 'downloadid', response['downloadid'], guid=guid)

                if self.update_status_snatched(guid, imdbid):
                    logging.info(u'Successfully sent {} to QBittorrent.'.format(title))
                    return {u'response': True, u'message': u'Sent to QBittorrent.', u'downloader': u'QBitorrent', u'downloadid': response['downloadid']}
                else:
                    return {u'response': False, u'error': u'Could not mark '
                            'search result as Snatched.'}
            else:
                return response

        # If sending to DelugeRPC
        delugerpc_conf = core.CONFIG['Downloader']['Torrent']['DelugeRPC']
        if delugerpc_conf['enabled'] is True:
            logging.info(u'Sending {} to DelugeRPC.'.format(kind))
            response = deluge.DelugeRPC.add_torrent(data)

            if response['response'] is True:

                # store downloadid in database
                self.sql.update('SEARCHRESULTS', 'downloadid', response['downloadid'], guid=guid)

                if self.update_status_snatched(guid, imdbid):
                    logging.info(u'Successfully sent {} to DelugeRPC.'.format(title))
                    return {u'response': True, u'message': u'Sent to Deluge.', u'downloader': u'Deluge', u'downloadid': response['downloadid']}
                else:
                    return {u'response': False, u'error': u'Could not mark '
                            'search result as Snatched.'}
            else:
                return response

        # If sending to DelugeWeb
        delugeweb_conf = core.CONFIG['Downloader']['Torrent']['DelugeWeb']
        if delugeweb_conf['enabled'] is True:
            logging.info(u'Sending {} to DelugeWeb.'.format(kind))
            response = deluge.DelugeWeb.add_torrent(data)

            if response['response'] is True:

                # store downloadid in database
                self.sql.update('SEARCHRESULTS', 'downloadid', response['downloadid'], guid=guid)

                if self.update_status_snatched(guid, imdbid):
                    logging.info(u'Successfully sent {} to DelugeWeb.'.format(title))
                    return {u'response': True, u'message': u'Sent to Deluge.', u'downloader': u'Deluge', u'downloadid': response['downloadid']}
                else:
                    return {u'response': False, u'error': u'Could not mark '
                            'search result as Snatched.'}
            else:
                return response

        # If sending to rTorrentSCGI
        rtorrent_conf = core.CONFIG['Downloader']['Torrent']['rTorrentSCGI']
        if rtorrent_conf['enabled'] is True:
            logging.info(u'Sending {} to rTorrent.'.format(kind))
            response = rtorrent.rTorrentSCGI.add_torrent(data)

            if response['response'] is True:

                # store downloadid in database
                self.sql.update('SEARCHRESULTS', 'downloadid', response['downloadid'], guid=guid)

                if self.update_status_snatched(guid, imdbid):
                    logging.info(u'Successfully sent {} to rTorrent.'.format(title))
                    return {u'response': True, u'message': u'Sent to rTorrent.', u'downloader': u'rTorrent', u'downloadid': response['downloadid']}
                else:
                    return {u'response': False, u'error': u'Could not mark '
                            'search result as Snatched.'}
            else:
                return response

        # If sending to rTorrentSCGI
        rtorrent_conf = core.CONFIG['Downloader']['Torrent']['rTorrentHTTP']
        if rtorrent_conf['enabled'] is True:
            logging.info(u'Sending {} to rTorrent.'.format(kind))
            response = rtorrent.rTorrentHTTP.add_torrent(data)

            if response['response'] is True:

                # store downloadid in database
                self.sql.update('SEARCHRESULTS', 'downloadid', response['downloadid'], guid=guid)

                if self.update_status_snatched(guid, imdbid):
                    logging.info(u'Successfully sent {} to rTorrent.'.format(title))
                    return {u'response': True, u'message': u'Sent to rTorrent.', u'downloader': u'rTorrent', u'downloadid': response['downloadid']}
                else:
                    return {u'response': False, u'error': u'Could not mark '
                            'search result as Snatched.'}
            else:
                return response

        else:
            return {u'response': False, u'error': u'No downloader enabled.'}

    def update_status_snatched(self, guid, imdbid):
        '''
        Updates MOVIES, SEARCHRESULTS, and MARKEDRESULTS to 'Snatched'
        Returns Bool on success/fail
        '''

        if not self.update.searchresults(guid, 'Snatched'):
            logging.error('Unable to update search result status to Snatched.')
            return False

        if not self.update.markedresults(guid, 'Snatched', imdbid=imdbid):
            logging.error('Unable to store marked search result as Snatched.')
            return False

        if not self.update.movie_status(imdbid):
            logging.error('Unable to update movie status to Snatched.')
            return False

        return True
