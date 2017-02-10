import json
import logging
import urllib2
from core.helpers import Comparisons
_k = Comparisons._k

logging = logging.getLogger(__name__)


class TMDB(object):

    def __init__(self):
        return

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
            return self._search_imdbid(search_term)
        else:
            movies = self._search_title(search_term)
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

        url = u'https://api.themoviedb.org/3/search/movie?api_key={}&page=1&include_adult=false&'.format(_k('tmdb'))

        if title[-4:].isdigit():
            query = u'query={}&year={}'.format(title[:-5], title[-4:])
        else:
            query = u'query={}'.format(title)

        search_string = url + query
        request = urllib2.Request(search_string, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            results = json.load(urllib2.urlopen(request))
            if results.get('success') == 'false':
                return None
            else:
                return results['results'][:6]
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'TMDB search.', exc_info=True)
            return ['']

    def _search_imdbid(self, imdbid):
        search_string = u'https://api.themoviedb.org/3/find/{}?api_key={}&language=en-US&external_source=imdb_id'.format(imdbid, _k('tmdb'))

        request = urllib2.Request(search_string, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            results = json.load(urllib2.urlopen(request))
            if results['movie_results'] == []:
                return None
            else:
                response = results['movie_results'][0]
                response['imdbid'] = imdbid
                return [response]
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'TMDB find.', exc_info=True)
            return {}

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
            logging.warning('Neither tmdbid or title supplied. Unable to find imdbid.')
            return None

        if not tmdbid:
            url = 'https://api.themoviedb.org/3/search/movie?api_key={}&language=en-US&query={}&year={}&page=1&include_adult=false'.format(_k('tmdb'), title, year).replace(' ', '+')
            request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                response = json.load(urllib2.urlopen(request))
                tmdbid = response['results'][0]['id']
                return response.get('imdb_id')
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e: # noqa
                logging.error(u'TMDB find.', exc_info=True)
                return None

        url = 'https://api.themoviedb.org/3/movie/{}?api_key={}'.format(tmdbid, _k('tmdb'))
        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            response = json.load(urllib2.urlopen(request))
            return response.get('imdb_id')
        except Exception, e: # noqa
            logging.error(u'TMDB get imdbid.', exc_info=True)
            return None


class Trailer(object):
    def get_trailer(self, title_date):
        ''' Gets trailer embed url from Youtube.
        :param title_date: str movie title and date ("Movie Title 2016")

        Attempts to connect 3 times in case Youtube is down or not responding
        Can fail if no response is recieved.

        Returns str or None
        '''

        search_term = (title_date + 'trailer').replace(' ', '+').encode('utf-8')

        search_string = "https://www.googleapis.com/youtube/v3/search?part=snippet&q={}&maxResults={}&key={}".format(search_term, '1', _k('youtube'))

        request = urllib2.Request(search_string, headers={'User-Agent': 'Mozilla/5.0'})

        tries = 0
        while tries < 3:
            try:
                data = urllib2.urlopen(request)
                data = json.load(data)
                return data['items'][0]['id']['videoId']
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e: # noqa
                logging.error(u'Tailer get_trailer.', exc_info=True)
                tries += 1
        return None
