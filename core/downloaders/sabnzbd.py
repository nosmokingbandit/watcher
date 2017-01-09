import json
import logging
import urllib2

import core

logging = logging.getLogger(__name__)


class Sabnzbd():

    @staticmethod
    def test_connection(data):
        ''' Tests connectivity to Sabnzbd
        :para data: dict of nzbget server information

        Tests if we can get Sab's stats using server info in 'data'

        Return True on success or str error message on failure
        '''

        host = data['sabhost']
        port = data['sabport']
        api = data['sabapi']

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

        Returns dict {'response': 'true', 'download_id': 'id'}
                     {'response': 'false', 'error': 'exception'}

        '''

        sab_conf = core.CONFIG['Sabnzbd']

        con_test = Sabnzbd.test_connection(sab_conf)
        if not con_test:
            d = {}
            d['status'] = con_test
            return d

        host = sab_conf['sabhost']
        port = sab_conf['sabport']
        api = sab_conf['sabapi']

        base_url = u'http://{}:{}/sabnzbd/api?apikey={}'.format(host, port, api)

        mode = u'addurl'
        name = urllib2.quote(data['guid'].encode('utf-8'))
        nzbname = urllib2.quote(data['title'].encode('ascii', 'ignore'))
        cat = sab_conf['sabcategory']
        priority_keys = {
            'Paused': '-2',
            'Low': '-1',
            'Normal': '0',
            'High': '1',
            'Forced': '2'
        }
        priority = priority_keys[sab_conf['sabpriority']]

        command_url = u'&mode={}&name={}&nzbname={}&cat={}&priority={}&output=json'.format(mode, name, nzbname, cat, priority)

        url = base_url + command_url

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            response = json.loads(urllib2.urlopen(request).read())

            if response['status'] is True and len(response['nzo_ids']) > 0:
                downloadid = response['nzo_ids'][0]
                return {'response': 'true', 'downloadid': downloadid}
            else:
                return {'response': 'false', 'error': 'Unable to add NZB.'}

        except Exception as e:
            return {'response': 'false', 'error': str(e.reason)}
