import logging
from xmlrpclib import ServerProxy

import core

logging = logging.getLogger(__name__)


class Nzbget():

    @staticmethod
    def test_connection(data):
        ''' Tests connectivity to Nzbget
        :para data: dict of nzbget server information

        Tests if we can get nzbget's version using server info in 'data'

        Return True on success or str error message on failure
        '''

        host = data['nzbghost']
        port = data['nzbgport']
        user = data['nzbguser']
        passw = data['nzbgpass']

        https = False
        if https:
            url = "https://{}:{}/{}:{}/xmlrpc".format(host, port, user, passw)
            nzbg_server = ServerProxy(url)
        else:
            url = "http://{}:{}/{}:{}/xmlrpc".format(host, port, user, passw)
            nzbg_server = ServerProxy(url)

        try:
            nzbg_server.version()
            return True
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'Nzbget test_connection', exc_info=True)
            return '{}.'.format(e)

    @staticmethod
    def add_nzb(data):
        ''' Adds nzb file to nzbget to download
        :param data: dict of nzb information

        Returns str response from server
        '''

        nzbg_conf = core.CONFIG['NzbGet']

        if not Nzbget.test_connection(nzbg_conf):
            return "Could not connect to NZBGet."

        host = nzbg_conf['nzbghost']
        port = nzbg_conf['nzbgport']
        user = nzbg_conf['nzbguser']
        passw = nzbg_conf['nzbgpass']

        https = False
        if https:
            url = "https://{}:{}/{}:{}/xmlrpc".format(host, port, user, passw)
        else:
            url = "http://{}:{}/{}:{}/xmlrpc".format(host, port, user, passw)

        nzbg_server = ServerProxy(url)

        filename = u'{}.nzb'.format(data['title'])
        contenturl = data['guid']
        category = nzbg_conf['nzbgcategory']
        priority_keys = {
            'Very Low': -100,
            'Low': -50,
            'Normal': 0,
            'High': 50,
            'Very High': 100,
            'Forced': 900
        }
        priority = priority_keys[nzbg_conf['nzbgpriority']]
        if nzbg_conf['nzbgaddpaused'] == u'true':
            paused = True
        else:
            paused = False
        dupekey = data['imdbid']
        dupescore = data['score']
        dupemode = u'All'

        try:
            response = nzbg_server.append(filename, contenturl, category, priority, False, paused, dupekey, dupescore, dupemode)
            return {'response': 'true', 'downloadid': response}

        except Exception, e:
            return {'response': 'false', 'error': str(e)}
