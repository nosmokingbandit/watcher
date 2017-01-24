import logging
import json
import urllib2
import zlib

from lib.deluge_client import DelugeRPCClient

import core
from core.helpers import Torrent

logging = logging.getLogger(__name__)


class DelugeRPC(object):

    @staticmethod
    def test_connection(data):
        ''' Tests connectivity to deluge daemon rpc
        data: dict of deluge server information

        Tests if we can open a socket to the rpc

        Return True on success or str error message on failure
        '''

        host = data['delugerpchost']
        port = int(data['delugerpcport'])
        user = data['delugerpcuser']
        password = data['delugerpcpass']

        client = DelugeRPCClient(host, port, user, password)
        try:
            error = client.connect()
            if error:
                return '{}.'.format(error)
        except Exception, e:
            return str(e)
        return True

    @staticmethod
    def add_torrent(data):
        ''' Adds torrent or magnet to Deluge
        data: dict of torrrent/magnet information

        Returns dict {'response': 'true', 'download_id': 'id'}
                     {'response': 'false', 'error': 'exception'}

        '''
        conf = core.CONFIG['DelugeRPC']

        host = conf['delugerpchost']
        port = int(conf['delugerpcport'])
        user = conf['delugerpcuser']
        password = conf['delugerpcpass']

        client = DelugeRPCClient(host, port, user, password)

        try:
            error = client.connect()
            if error:
                return {'response': 'false', 'error': error}
        except Exception, e:
            return {'response': 'false', 'error': str(e)}

        try:
            def_download_path = client.call('core.get_config')['download_location']
        except Exception, e:
            logging.error('Unable to get download path.', exc_info=True)
            return {'response': 'false', 'error': 'Unable to get download path.'}

        download_path = '{}/{}'.format(def_download_path, conf['delugerpccategory'])

        priority_keys = {
            'Normal': 0,
            'High': 128,
            'Max': 255
        }

        options = {}
        options['add_paused'] = conf['delugerpcaddpaused'] == u'true'
        options['download_location'] = download_path
        options['priority'] = priority_keys[conf['delugerpcpriority']]

        if data['type'] == u'magnet':
            try:
                download_id = client.call('core.add_torrent_magnet', data['torrentfile'], options)
                return {'response': 'true', 'downloadid': download_id}
            except Exception, e:
                logging.error('Unable to send magnet.', exc_info=True)
                return {'response': 'false', 'error': str(e)}
        elif data['type'] == u'torrent':
            try:
                download_id = client.call('core.add_torrent_url', data['torrentfile'], options)
                return {'response': 'true', 'downloadid': download_id}
            except Exception, e:
                logging.error('Unable to send magnet.', exc_info=True)
                return {'response': 'false', 'error': str(e)}
        return


class DelugeWeb(object):

    cookie = None
    retry = False
    command_id = 0

    @staticmethod
    def test_connection(data):
        ''' Tests connectivity to deluge web client
        data: dict of deluge server information


        Return True on success or str error message on failure
        '''

        host = data['delugewebhost']
        port = int(data['delugewebport'])
        password = data['delugewebpass']

        url = u'{}:{}/json'.format(host, port)

        return DelugeWeb._login(url, password)

    @staticmethod
    def add_torrent(data):
        ''' Adds torrent or magnet to deluge web api
        data: dict of torrrent/magnet information

        Adds torrents to default/path/<category>

        Returns dict {'response': 'true', 'download_id': 'id'}
                     {'response': 'false', 'error': 'exception'}

        '''

        deluge_conf = core.CONFIG['DelugeWeb']

        host = deluge_conf['delugewebhost']
        port = deluge_conf['delugewebport']
        url = '{}:{}/json'.format(host, port)

        # check cookie validity while getting default download dir
        download_dir = DelugeWeb._get_download_dir(url)

        if not download_dir:
            password = deluge_conf['delugewebpass']
            if DelugeWeb._login(url, password) is not True:
                return {'response': 'false', 'error': 'Incorrect usename or password.'}

        download_dir = DelugeWeb._get_download_dir(url)

        if not download_dir:
            return {'response': 'false', 'error': 'Unable to get path information.'}
        # if we got download_dir we can connect.

        download_dir = '{}/{}'.format(download_dir, deluge_conf['delugewebcategory'])

        priority_keys = {
            'Normal': 0,
            'High': 128,
            'Max': 255
        }

        torrent = {'path': data['torrentfile'], 'options': {}}
        torrent['options']['add_paused'] = deluge_conf['delugewebaddpaused'] == u'true'
        torrent['options']['download_location'] = download_dir
        torrent['options']['priority'] = priority_keys[deluge_conf['delugewebpriority']]

        command = {'method': 'web.add_torrents',
                   'params': [[torrent]],
                   'id': DelugeWeb.command_id
                   }
        DelugeWeb.command_id += 1

        post_data = json.dumps(command)
        request = urllib2.Request(url, post_data, headers={'User-Agent': 'Mozilla/5.0'})
        request.add_header('cookie', DelugeWeb.cookie)

        try:
            response = DelugeWeb._read(urllib2.urlopen(request))
            if response['result'] is True:
                downloadid = Torrent.get_hash(data['torrentfile'])
                return {'response': 'true', 'downloadid': downloadid}
            else:
                return {'response': 'false', 'error': response['error']}
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'Delugeweb add_torrent', exc_info=True)
            return {'response': 'false', 'error': str(e)}

    @staticmethod
    def _get_download_dir(url):

        command = {'method': 'core.get_config_value',
                   'params': ['download_location'],
                   'id': DelugeWeb.command_id
                   }
        DelugeWeb.command_id += 1

        post_data = json.dumps(command)

        request = urllib2.Request(url, post_data, headers={'User-Agent': 'Mozilla/5.0'})
        request.add_header('cookie', DelugeWeb.cookie)

        try:
            response = DelugeWeb._read(urllib2.urlopen(request))
            return response['result']
        except urllib2.HTTPError:
            return False
        except Exception, e:
            logging.error(u'delugeweb get_download_dir', exc_info=True)
            return {'response': 'false', 'error': str(e.reason)}

    @staticmethod
    def _read(response):
        ''' Reads gzipped json response into dict
        '''

        return json.loads(zlib.decompress(response.read(), 16+zlib.MAX_WBITS))

    @staticmethod
    def _login(url, password):

        command = {'method': 'auth.login',
                   'params': [password],
                   'id': DelugeWeb.command_id
                   }
        DelugeWeb.command_id += 1

        post_data = json.dumps(command)

        request = urllib2.Request(url, post_data, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            response = urllib2.urlopen(request)
            DelugeWeb.cookie = response.headers.get('Set-Cookie')

            if DelugeWeb.cookie is None:
                return 'Incorrect password.'

            if response.msg == 'OK':
                return True
            else:
                return response.msg

            return True
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'DelugeWeb test_connection', exc_info=True)
            return '{}.'.format(e.reason)
