import logging

from lib import transmissionrpc

import core

logging = logging.getLogger(__name__)


class Transmission(object):

    @staticmethod
    def test_connection(data):
        ''' Tests connectivity to Transmission
        data: dict of Transmission server information

        Return True on success or str error message on failure
        '''

        host = data['transmissionhost']
        port = data['transmissionport']
        user = data['transmissionuser']
        password = data['transmissionpass']

        try:
            client = transmissionrpc.Client(host, port, user=user, password=password)
            if type(client.rpc_version) == int:
                return True
            else:
                return 'Unable to connect.'
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'Transmission test_connection', exc_info=True)
            return '{}.'.format(e)

    @staticmethod
    def add_torrent(data):
        ''' Adds torrent or magnet to Transmission
        data: dict of torrrent/magnet information

        Adds torrents to /default/path/<category>

        Returns dict {'response': 'true', 'download_id': 'id'}
                     {'response': 'false', 'error': 'exception'}

        '''

        trans_conf = core.CONFIG['Transmission']

        host = trans_conf['transmissionhost']
        port = trans_conf['transmissionport']
        user = trans_conf['transmissionuser']
        password = trans_conf['transmissionpass']

        client = transmissionrpc.Client(host, port, user=user, password=password)

        url = data['torrentfile']
        paused = trans_conf['transmissionaddpaused'] == 'true'
        bandwidthPriority = trans_conf['transmissionpriority']
        category = trans_conf['transmissioncategory']

        priority_keys = {
            'Low': '-1',
            'Normal': '0',
            'High': '1'
        }

        bandwidthPriority = priority_keys[trans_conf['transmissionpriority']]

        download_dir = None
        if category:
            d = client.get_session().__dict__['_fields']['download_dir'][0]
            d_components = d.split('/')
            d_components.append(category)

            download_dir = '/'.join(d_components)

        try:
            download = client.add_torrent(url, paused=paused, bandwidthPriority=bandwidthPriority, download_dir=download_dir, timeout=30)
            download_id = download.hashString
            return {'response': 'true', 'downloadid': download_id}
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'Transmission add_torrent', exc_info=True)
            return {'response': 'false', 'error': str(e)}
