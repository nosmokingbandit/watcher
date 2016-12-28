import json
import logging

import cherrypy
import core
from core import ajax, sqldb

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
        self.ajax = ajax.Ajax()
        return

    def GET(self, **params):
        serverkey = core.CONFIG['Server']['apikey']

        if 'apikey' not in params:
            logging.warning('API request failed, no key supplied.')
            return 'No API key supplied.'

        # check for api key
        if serverkey != params['apikey']:
            logging.warning('Invalid API key in request: {}'.format(params['apikey']))
            return 'Incorrect API Key.'

        # find what we are going to do
        if 'mode' not in params:
            return 'No API mode specified.'

        if params['mode'] == 'liststatus':

            if 'imdbid' in params:
                return self.liststatus(imdbid=params['imdbid'])
            else:
                return self.liststatus()

        elif params['mode'] == 'addmovie':
            if 'imdbid' not in params:
                return 'No IMDBID supplied.'
            else:
                imdbid = params['imdbid']
            return self.addmovie(imdbid)
        elif params['mode'] == 'removemovie':
            if 'imdbid' not in params:
                return 'No IMDBID supplied.'
            else:
                imdbid = params['imdbid']
            return self.removemovie(imdbid)
        elif params['mode'] == 'version':
            return self.getversion()
        
        else:
            return 'Invalid mode.'

    def liststatus(self, imdbid=None):
        logging.info('API request movie list.')
        lst = []
        movies = self.sql.get_user_movies()
        if not movies:
            return 'No movies found.'

        if imdbid:
            for i in movies:
                if i['imdbid'] == imdbid:
                    return json.dumps(i, indent=1)
        else:
            for movie in movies:
                lst.append(dict(movie))
                return json.dumps(lst, indent=1)

    def addmovie(self, imdbid):
        logging.info('API request add movie {}'.format(imdbid))
        return self.ajax.quick_add(imdbid)

    def removemovie(self, imdbid):
        logging.info('API request remove movie {}'.format(imdbid))
        response = self.ajax.remove_movie(imdbid)
        return json.dumps(response, indent=1)

    def getversion(self):
        if core.CURRENT_HASH is not None:
            return '[{"version":"'+core.CURRENT_HASH[0:7]+'"}]'
        else:
            return 'updating...'    
