import core
import urllib2
import json

import logging
logging = logging.getLogger(__name__)

class Sabnzbd():

    @staticmethod
    def test_connection(data):

        host = data['sabhost']
        port = data['sabport']
        api = data['sabapi']

        url = 'http://{}:{}/sabnzbd/api?apikey={}&mode=server_stats'.format(host, port, api)

        request = urllib2.Request( url, headers={'User-Agent' : 'Mozilla/5.0'} )

        try:
            response = urllib2.urlopen(request).read()
            if 'error' in response:
                return response
            return True
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error('Sabnzbd test_connection', exc_info=True)
            return '{}. \n\n Please review your settings.'.format(e.reason)

    # returns dict {'status': <>, 'nzo_ids': [<>] }
    @staticmethod
    def add_nzb(data):
        sab_conf = core.CONFIG['Sabnzbd']

        con_test = Sabnzbd.test_connection(sab_conf)
        if con_test != True:
            d = {}
            d['status'] = con_test
            return d


        host = sab_conf['sabhost']
        port = sab_conf['sabport']
        api = sab_conf['sabapi']

        base_url = 'http://{}:{}/sabnzbd/api?apikey={}'.format(host, port, api)

        mode = 'addurl'
        name =  urllib2.quote(data['guid'].encode('utf-8'))
        nzbname = urllib2.quote('{}.watcher'.format(data['title']))
        cat = sab_conf['sabcategory']
        priority_keys = {
            'Paused': '-2',
            'Low': '-1',
            'Normal': '0',
            'High': '1',
            'Force': '2'
        }
        priority = priority_keys[sab_conf['sabpriority']]

        command_url = '&mode={}&name={}&nzbname={}&cat={}&priority={}&output=json'.format(mode, name, nzbname, cat, priority)

        url =  base_url + command_url

        request = urllib2.Request( url, headers={'User-Agent' : 'Mozilla/5.0'} )

        try:
            response = json.loads( urllib2.urlopen(request).read() )
            return response

        except Exception as err:
            response = {}
            response['status'] = err
            return response
