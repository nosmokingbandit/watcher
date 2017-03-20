import logging
import json
import urllib
import urllib2

import core
from core.helpers import Torrent, Url

logging = logging.getLogger(__name__)


class QBittorrent(object):

    cookie = None
    retry = False

    @staticmethod
    def test_connection(data):
        ''' Tests connectivity to qbittorrent
        data: dict of qbittorrent server information

        Return True on success or str error message on failure
        '''

        host = data['host']
        port = data['port']
        user = data['user']
        password = data['pass']

        url = u'{}:{}/'.format(host, port)

        return QBittorrent._login(url, user, password)

    @staticmethod
    def add_torrent(data):
        ''' Adds torrent or magnet to qbittorrent
        data: dict of torrrent/magnet information

        Adds torrents to default/path/<category>

        Returns dict {'response': True, 'download_id': 'id'}
                     {'response': False, 'error': 'exception'}

        '''

        conf = core.CONFIG['Downloader']['Torrent']['QBittorrent']

        host = conf['host']
        port = conf['port']
        base_url = u'{}:{}/'.format(host, port)

        user = conf['user']
        password = conf['pass']

        # check cookie validity while getting default download dir
        download_dir = QBittorrent._get_download_dir(base_url)

        if not download_dir:
            if QBittorrent._login(base_url, user, password) is not True:
                return {'response': False, 'error': 'Incorrect usename or password.'}

        download_dir = QBittorrent._get_download_dir(base_url)

        if not download_dir:
            return {'response': False, 'error': 'Unable to get path information.'}
        # if we got download_dir we can connect.

        post_data = {}

        post_data['urls'] = data['torrentfile']

        post_data['savepath'] = u'{}{}'.format(download_dir, conf['category'])

        post_data['category'] = conf['category']

        url = u'{}command/download'.format(base_url)
        post_data = urllib.urlencode(post_data)
        request = Url.request(url, post_data=post_data)
        request.add_header('cookie', QBittorrent.cookie)

        try:
            Url.open(request)  # QBit returns an empty string
            downloadid = Torrent.get_hash(data['torrentfile'])
            return {'response': True, 'downloadid': downloadid}
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'QBittorrent connection test failed.', exc_info=True)
            return {'response': False, 'error': str(e.reason)}

    @staticmethod
    def _get_download_dir(base_url):
        try:
            url = u'{}query/preferences'.format(base_url)
            request = Url.request(url)
            request.add_header('cookie', QBittorrent.cookie)
            response = json.loads(Url.open(request))
            return response['save_path']
        except urllib2.HTTPError:
            return False
        except Exception, e:
            logging.error(u'QBittorrent unable to get download dir.', exc_info=True)
            return {'response': False, 'error': str(e.reason)}

    @staticmethod
    def get_torrents(base_url):
        url = u'{}query/torrents'.format(base_url)
        request = Url.request(url)
        request.add_header('cookie', QBittorrent.cookie)
        return Url.open(request)

    @staticmethod
    def _login(url, username, password):

        data = {'username': username,
                'password': password
                }

        post_data = urllib.urlencode(data)

        url = u'{}login'.format(url)
        request = Url.request(url, post_data=post_data)

        try:
            response = urllib2.urlopen(request)
            QBittorrent.cookie = response.headers.get('Set-Cookie')
            result = response.read()
            response.close()

            if result == 'Ok.':
                return True
            elif result == 'Fails.':
                return u'Incorrect usename or password'
            else:
                return result

        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'qbittorrent test_connection', exc_info=True)
            return u'{}.'.format(str(e.reason))
