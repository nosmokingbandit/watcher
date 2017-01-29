import core
from core import ajax, config, sqldb
from core.movieinfo import TMDB
import json
import logging
import urllib2

logging = logging.getLogger(__name__)


class PopularMoviesFeed(object):
    def __init__(self):
        self.config = config.Config()
        self.tmdb = TMDB()
        self.sql = sqldb.SQL()
        self.ajax = ajax.Ajax()
        return

    def get_feed(self):
        ''' Gets feed from popular-movies (https://github.com/sjlu/popular-movies)

        Gets raw feed (JSON), sends to self.parse_xml to turn into dict

        Returns True or None on success or failure (due to exception or empty movie list)
        '''

        logging.info(u'Syncing popular movie feed')
        request = urllib2.Request('https://s3.amazonaws.com/popular-movies/movies.json',
                                  headers={'User-Agent': 'Mozilla/5.0'})
        try:
            response = urllib2.urlopen(request).read()
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Popular feed request.', exc_info=True)
            return None

        movies = json.loads(response)

        if movies:
            logging.info(u'Found {} movies in popular movies.'.format(len(movies)))
            self.sync_new_movies(movies)
            logging.info(u'Popular movies sync complete.')
            return True
        else:
            return None

    def sync_new_movies(self, movies):
        ''' Adds new movies from rss feed
        :params movies: list of dicts of movies

        Checks last sync time and pulls new imdbids from feed.

        Checks if movies are already in library and ignores.

        Executes ajax.add_wanted_movie() for each new imdbid

        Does not return
        '''

        new_sync_movies = []
        for i in movies:

            title = i['title']
            imdbid = i['imdb_id']

            logging.info(u'Found new watchlist movie: {} {}'.format(title, imdbid))

            new_sync_movies.append(imdbid)

        # check if movies already exists

        existing_movies = [i['imdbid'] for i in self.sql.get_user_movies()]

        movies_to_add = [i for i in new_sync_movies if i not in existing_movies]

        # do quick-add procedure
        quality = {}
        quality['Quality'] = core.CONFIG['Quality']
        for imdbid in movies_to_add:
            movie_info = self.tmdb.find_imdbid(imdbid)[0]
            if not movie_info:
                logging.info(u'{} not found on TMDB. Cannot add.'.format(imdbid))
                continue
            # logging.info(u'Adding {}'.format(imdbid))
            movie_info['quality'] = json.dumps(quality)
            self.ajax.add_wanted_movie(json.dumps(movie_info))
