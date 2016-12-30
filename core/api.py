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
            return json.dumps({'response': 'false',
                               'error': 'no api key supplied'})

        # check for api key
        if serverkey != params['apikey']:
            logging.warning('Invalid API key in request: {}'.format(params['apikey']))
            return json.dumps({'response': 'false',
                               'error': 'incorrect api key'})

        # find what we are going to do
        if 'mode' not in params:
            return json.dumps({'response': 'false',
                               'error': 'no api mode specified'})

        if params['mode'] == 'liststatus':

            if 'imdbid' in params:
                return self.liststatus(imdbid=params['imdbid'])
            else:
                return self.liststatus()

        elif params['mode'] == 'addmovie':
            if 'imdbid' not in params:
                return json.dumps({'response': 'false',
                                   'error': 'no imdbid supplied'})
            else:
                imdbid = params['imdbid']
            return self.addmovie(imdbid)

        elif params['mode'] == 'removemovie':
            if 'imdbid' not in params:
                return json.dumps({'response': 'false',
                                   'error': 'no imdbid supplied'})
            else:
                imdbid = params['imdbid']
            return self.removemovie(imdbid)

        elif params['mode'] == 'version':
            return self.version()

        else:
            return json.dumps({'response': 'false',
                               'error': 'invalid mode'})

    def liststatus(self, imdbid=None):
        ''' Returns status of user's movies
        :param imdbid: imdb id number of movie <optional>

        Returns list of movie details from MOVIES table. If imdbid is not supplied
            returns all movie details.

        Returns str json.dumps(list) or json.dumps(dict) for single movie
        '''
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
        ''' Add movie with default quality settings
        :param imdbid: imdb id number of movie

        Returns ## WHAT DOES THIS RETURN?
        '''

        logging.info('API request add movie {}'.format(imdbid))
        return self.ajax.quick_add(imdbid)

    def removemovie(self, imdbid):
        ''' Remove movie from wanted list
        :param imdbid: imdb id number of movie

        Returns ## WHAT DOES THIS RETURN?
        '''
        logging.info('API request remove movie {}'.format(imdbid))
        response = self.ajax.remove_movie(imdbid)
        return json.dumps(response, indent=1)

    def version(self):
        ''' Simple endpoint to return commit hash

        Mostly used to test connectivity without modifying the server.

        Returns str json.dumps(dict)
        '''
        return json.dumps({'response': 'true', 'version': core.CURRENT_HASH})
