import json
import cherrypy
import core
from core import sqldb

import logging
logging = logging.getLogger(__name__)


class API(object):
    '''
    A simple GET/POST api. Used for basic remote interactions.
    This still needs work.
    '''
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    exposed = True

    def __init__(self):
        self.sql = sqldb.SQL()

    def GET(self, **params):
        serverkey = core.CONFIG['Server']['apikey']

        # check for api key
        if serverkey != params['apikey']:
            logging.warning('Invalid API key in request.')
            return 'Incorrect API Key.'

        # find what we are going to do
        if 'mode' not in params:
            return 'No API mode specified.'

        if params['mode'] == 'liststatus':
            return self.liststatus()

    def liststatus(self):
        logging.info('API request movie list.')
        l = []
        movies = self.sql.get_user_movies()
        if not movies:
            return l
        else:
            for movie in movies:
                l.append(dict(movie))
            return json.dumps(l, indent=1)





