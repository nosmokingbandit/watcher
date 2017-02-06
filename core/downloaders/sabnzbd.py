import json
import logging
import urllib2

import core

logging = logging.getLogger(__name__)


class Sabnzbd():

    @staticmethod
    def test_connection(data):
        ''' Tests connectivity to Sabnzbd
        :para data: dict of Sab server information

        Tests if we can get Sab's stats using server info in 'data'

        Return True on success or str error message on failure
        '''

        host = data['host']
        port = data['port']
        api = data['api']

        url = u'http://{}:{}/sabnzbd/api?apikey={}&mode=server_stats'.format(host, port, api)

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            response = urllib2.urlopen(request).read()
            if 'error' in response:
                return response
            return True
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'Sabnzbd test_connection', exc_info=True)
            return '{}.'.format(e.reason)

    # returns dict {'status': <>, 'nzo_ids': [<>] }
    @staticmethod
    def add_nzb(data):
        ''' Adds nzb file to sab to download
        :param data: dict of nzb information

        Returns dict {'response': True, 'download_id': 'id'}
                     {'response': False, 'error': 'exception'}

        '''

        conf = core.CONFIG['Downloader']['Usenet']['Sabnzbd']

        host = conf['host']
        port = conf['port']
        api = conf['api']

        base_url = u'http://{}:{}/sabnzbd/api?apikey={}'.format(host, port, api)

        mode = u'addurl'
        name = urllib2.quote(data['guid'].encode('utf-8'))
        nzbname = urllib2.quote(data['title'].encode('ascii', 'ignore'))
        cat = conf['category']
        priority_keys = {
            'Paused': '-2',
            'Low': '-1',
            'Normal': '0',
            'High': '1',
            'Forced': '2'
        }
        priority = priority_keys[conf['priority']]

        command_url = u'&mode={}&name={}&nzbname={}&cat={}&priority={}&output=json'.format(mode, name, nzbname, cat, priority)

        url = base_url + command_url

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            response = json.loads(urllib2.urlopen(request).read())

            if response['status'] is True and len(response['nzo_ids']) > 0:
                downloadid = response['nzo_ids'][0]
                return {'response': True, 'downloadid': downloadid}
            else:
                return {'response': False, 'error': 'Unable to add NZB.'}

        except Exception as e:
            return {'response': False, 'error': str(e.reason)}
