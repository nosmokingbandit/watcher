import logging
import json
import urllib
import urllib2

import core
from core.helpers import Torrent

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
        base_url = '{}:{}/'.format(host, port)

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

        post_data['savepath'] = '{}{}'.format(download_dir, conf['category'])

        post_data['category'] = conf['category']

        req_url = u'{}command/download'.format(base_url)
        post_data = urllib.urlencode(post_data)
        request = urllib2.Request(req_url, post_data, headers={'User-Agent': 'Mozilla/5.0'})
        request.add_header('cookie', QBittorrent.cookie)

        try:
            urllib2.urlopen(request)  # QBit returns an empty string
            downloadid = Torrent.get_hash(data['torrentfile'])
            return {'response': True, 'downloadid': downloadid}
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'qbittorrent test_connection', exc_info=True)
            return {'response': False, 'error': str(e.reason)}

    @staticmethod
    def _get_download_dir(base_url):
        try:
            url = u'{}query/preferences'.format(base_url)
            request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            request.add_header('cookie', QBittorrent.cookie)
            response = json.loads(urllib2.urlopen(request).read())
            return response['save_path']
        except urllib2.HTTPError:
            return False
        except Exception, e:
            logging.error(u'qbittorrent get_download_dir', exc_info=True)
            return {'response': False, 'error': str(e.reason)}

    @staticmethod
    def get_torrents(base_url):
        url = u'{}query/torrents'.format(base_url)
        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        request.add_header('cookie', QBittorrent.cookie)
        return urllib2.urlopen(request).read()

    @staticmethod
    def _login(url, username, password):

        data = {'username': username,
                'password': password
                }

        post_data = urllib.urlencode(data)

        url = u'{}login'.format(url)
        request = urllib2.Request(url, post_data, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            response = urllib2.urlopen(request)
            QBittorrent.cookie = response.headers.get('Set-Cookie')
            response = response.read()

            if response == 'Ok.':
                return True
            elif response == 'Fails.':
                return u'Incorrect usename or password'
            else:
                return response

        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'qbittorrent test_connection', exc_info=True)
            return u'{}.'.format(str(e.reason))


'''
{
u'category': u'Watcher',
u'num_incomplete': -1,
u'num_complete': -1,
u'force_start': False,
u'hash': u'e1e8bc80e9e34547661d16f03d10756421d8278c',
u'name': u'Toy Story 3 (BDrip 1080p ENG-ITA DTS) X264 bluray (2010)',
u'completion_on': 4294967295L,
u'super_seeding': False,
u'seq_dl': False,
u'num_seeds': 0,
u'upspeed': 0,
u'priority': 1,
u'state': u'pausedDL',
u'eta': 8640000,
u'added_on': 1484858904,
u'save_path': u'C:\\Users\\Steven\\Downloads\\',
u'num_leechs': 0,
u'progress': 0,
u'size': 0,
u'dlspeed': 0,
u'ratio': 0
}
'''
