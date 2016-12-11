import core
from xmlrpclib import ServerProxy

import logging
logging = logging.getLogger(__name__)

class Nzbget():

    @staticmethod
    def test_connection(data):

        host = data['nzbghost']
        port = data['nzbgport']
        user = data['nzbguser']
        passw = data['nzbgpass']

        https = False
        if https:
            url = "https://{}:{}@{}:{}/xmlrpc".format(user, passw, host, port)
            nzbg_server = ServerProxy(url)
        else:
            url = "http://{}:{}@{}:{}/xmlrpc".format(user, passw, host, port)
            nzbg_server = ServerProxy(url)

        try:
            nzbg_server.version()
            return True
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error('Nzbget test_connection', exc_info=True)
            return '{}. \n\n Please review your settings.'.format(e)

    @staticmethod
    def add_nzb(data):
        nzbg_conf = core.CONFIG['NzbGet']

        if not Nzbget.test_connection(nzbg_conf):
            return "Could not connect to NZBGet."

        host = nzbg_conf['nzbghost']
        port = nzbg_conf['nzbgport']
        user = nzbg_conf['nzbguser']
        passw = nzbg_conf['nzbgpass']

        https = False
        if https:
            url = "https://{}:{}@{}:{}/xmlrpc".format(user, passw, host, port)
        else:
            url = "http://{}:{}@{}:{}/xmlrpc".format(user, passw, host, port)

        nzbg_server = ServerProxy(url)

        filename = '{}.watcher.nzb'.format(data['title'])
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
        if nzbg_conf['nzbgaddpaused'] == 'true':
            paused = True
        else:
            paused = False
        dupekey = data['imdbid']
        dupescore = data['score']
        dupemode = 'All'

        response = nzbg_server.append(filename, contenturl, category, priority, False, paused, dupekey, dupescore, dupemode)

        return response


