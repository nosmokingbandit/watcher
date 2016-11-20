import json
import cherrypy
import urllib2
from urlparse import parse_qs
from core import config, sqldb, snatcher, postprocessing

import logging
logging = logging.getLogger(__name__)

class API(object):
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    exposed = True

    def __init__(self):
        self.conf = config.Config()
        self.sql = sqldb.SQL()
        self.post = postprocessing.PostProcessing()


    def GET(self, params):
        serverkey = self.conf['Server']['apikey']
        params = parse_qs(params)
        for k, v in params.iteritems():
            params[k] = v[0]

        if serverkey != params['apikey']:
            logging.warning('Invalid API key in request.')
            return 'Incorrect API Key.'

        if 'mode' not in params:
            return 'No API mode specified.'
        if params['mode'] == 'liststatus':
            logging.info('API request movie list.')
            movies = self.sql.get_user_movies()
            l = []
            for movie in movies:
                l.append(dict(movie))
            return json.dumps(l, indent=1)

        if 'guid' not in params:
            return 'No GUID Supplied. Something went wrong with the postprocessing script.'

        guid = urllib2.unquote(params['guid'])
        if params['mode'] == 'failed':
            return self.post.failed(guid)
        if params['mode'] == 'complete':
            path = urllib2.unquote(params['path'])
            return self.post.complete(guid, path)






