import json
import logging
import urllib2
from time import time, sleep
from core.helpers import Comparisons, Url
import core
_k = Comparisons._k

logging = logging.getLogger(__name__)


class TMDB(object):

    def __init__(self):
        self.cap = 30
        if not core.TMDB_LAST_FILL:
            core.TMDB_LAST_FILL = time()
        return

    def get_tokens(self):
        if core.TMDB_TOKENS < self.cap:
            now = time()
            if (now - core.TMDB_LAST_FILL) > 10:
                core.TMDB_TOKENS = self.cap
            core.TMDB_LAST_FILL = time()
        return core.TMDB_TOKENS

    def use_token(self):
        core.TMDB_TOKENS -= 1

    def search(self, search_term, single=False):
        ''' Search TMDB for all matches
        :param search_term: str title of movie to search for.
        single: bool return only first result   <default False>

        Can accept imdbid, title, or title year.

        Passes term to find_imdbid or find_title depending on the data recieved.

        Returns list of dicts of individual movies from the find_x function.
        If single==True, returns dict of single result
        '''

        search_term = search_term.replace(" ", "+")

        if search_term[:2] == u'tt' and search_term[2:].isdigit():
            movies = self._search_imdbid(search_term)
        elif search_term.isdigit():
            movies = self._search_tmdbid(search_term)
        else:
            movies = self._search_title(search_term)

        if not movies:
            return None
        if single is True:
            return movies[0]
        else:
            return movies

    def _search_title(self, title):
        ''' Search TMDB for title
        title: str movie title

        Title can include year ie Move Title 2017

        Returns list results or str error/fail message
        '''

        title = Url.encode(title)

        url = u'https://api.themoviedb.org/3/search/movie?api_key={}&page=1&include_adult=false&'.format(_k('tmdb'))
        if title[-4:].isdigit():
            query = u'query={}&year={}'.format(title[:-5], title[-4:])
        else:
            query = u'query={}'.format(title)

        url = url + query
        request = Url.request(url)

        while self.get_tokens() < 3:
            sleep(0.3)
        self.use_token()

        try:
            results = json.load(urllib2.urlopen(request))
            if results.get('success') == 'false':
                return None
            else:
                return results['results'][:6]
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Error searching for title on TMDB.', exc_info=True)
            return ['']

    def _search_imdbid(self, imdbid):

        url = u'https://api.themoviedb.org/3/find/{}?api_key={}&language=en-US&external_source=imdb_id'.format(imdbid, _k('tmdb'))
        request = Url.request(url)

        while self.get_tokens() < 3:
            sleep(0.5)
        self.use_token()

        try:
            results = json.load(urllib2.urlopen(request))
            if results['movie_results'] == []:
                return ['']
            else:
                response = results['movie_results'][0]
                response['imdbid'] = imdbid
                return [response]
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Error searching for IMDBID on TMDB.', exc_info=True)
            return ['']

    def _search_tmdbid(self, tmdbid):

        url = u'https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US'.format(tmdbid, _k('tmdb'))
        request = Url.request(url)

        while self.get_tokens() < 3:
            sleep(0.3)
        self.use_token()

        try:
            response = json.load(urllib2.urlopen(request))
            if response.get('status_code'):
                return ['']
            else:
                return [response]
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Error searching for TMDBID on TMDB.', exc_info=True)
            return ['']

    def get_imdbid(self, tmdbid=None, title=None, year=''):
        ''' Gets imdbid from tmdbid
        tmdbid: str TMDB movie id #
        title: str movie title
        year str year of movie release

        MUST supply either tmdbid or title. Year is optional with title, but results
            are more reliable with it.

        Returns str imdbid or None on failure
        '''

        if not tmdbid and not title:
            logging.warning(u'Neither tmdbid or title supplied. Unable to find imdbid.')
            return None

        if not tmdbid:
            title = Url.encode(title)
            year = Url.encode(year)

            url = u'https://api.themoviedb.org/3/search/movie?api_key={}&language=en-US&query={}&year={}&page=1&include_adult=false'.format(_k('tmdb'), title, year)
            request = Url.request(url)

            while self.get_tokens() < 3:
                sleep(0.3)
            self.use_token()

            try:
                response = json.load(urllib2.urlopen(request))
                results = response['results']
                if results:
                    tmdbid = results[0]['id']
                else:
                    return None
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e: # noqa
                logging.error(u'Error attempting to get TMDBID from TMDB.', exc_info=True)
                return None

        url = u'https://api.themoviedb.org/3/movie/{}?api_key={}'.format(tmdbid, _k('tmdb'))
        request = Url.request(url)

        while self.get_tokens() < 3:
            sleep(0.3)
        self.use_token()

        try:
            response = json.load(urllib2.urlopen(request))
            return response.get('imdb_id')
        except Exception, e: # noqa
            logging.error(u'Error attempting to get IMDBID from TMDB.', exc_info=True)
            return None


class Trailer(object):
    def get_trailer(self, title_date):
        ''' Gets trailer embed url from Youtube.
        :param title_date: str movie title and date ("Movie Title 2016")

        Attempts to connect 3 times in case Youtube is down or not responding
        Can fail if no response is recieved.

        Returns str or None
        '''

        search_term = Url.encode((title_date + '+trailer'))

        search_string = u"https://www.googleapis.com/youtube/v3/search?part=snippet&q={}&maxResults=1&key={}".format(search_term, _k('youtube'))

        request = Url.request(search_string)

        tries = 0
        while tries < 3:
            try:
                data = urllib2.urlopen(request)
                data = json.load(data)
                return data['items'][0]['id']['videoId']
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e: # noqa
                if tries == 2:
                    logging.error(u'Unable to get trailer from Youtube.', exc_info=True)
                tries += 1
        return None
