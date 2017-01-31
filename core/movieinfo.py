import json
import logging
import urllib2
from core import sqldb
from core.helpers import Comparisons
_k = Comparisons._k

logging = logging.getLogger(__name__)


class OMDB(object):

    def __init__(self):
        return

    def get_info(self, title=None, year=None, imdbid=None, tags=[]):
        ''' Search OMDB for every key in tags
        title: str title of movie <optional>
        year: str year of movie's release_date <optional>
        imdbid: imdb id # <optional>
        tags: list or tuple of strings to pull from OMDB json

        Finds movie in OMDB using imdbid, or title and year, then looks in json for all
            keys in 'tags' and returns them as a tuple.

        Either imdbid or title *and* year must be supplied. If not, returns None.

        It is advised to use imdbid when possible.

        Any returned value can be None.

        Will *ALWAYS* return tuple, even in fail conditions. Test the data in the calling method.

        Returns tuple matching 'tags'.

        '''

        if not tags:
            return (None)
        else:
            length = len(tags)

        if imdbid:
            search_string = u'http://www.omdbapi.com/?i={}&r=json'.format(imdbid)
        elif title and year:
            title = ''.join([i if ord(i) < 128 else '+' for i in title])
            search_string = u'http://www.omdbapi.com/?t={}&y={}&r=json'.format(title, year).replace(' ', '+')
        else:
            return self._null_tuple(length)

        request = urllib2.Request(search_string, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            result = json.load(urllib2.urlopen(request))
            if result['Response'] == u'False':
                return self._null_tuple(length)
            else:
                response = []
                for tag in tags:
                    response.append(result.get(tag))
                return tuple(response)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'OMDB search.', exc_info=True)
            return self._null_tuple(length)

    def _null_tuple(self, length):
        return (None,) * length


class TMDB(object):

    def __init__(self):
        return

    def search(self, search_term):
        ''' Search TMDB for all matches
        :param search_term: str title of movie to search for.

        Can accept imdbid, title, or title year.

        Passes term to find_imdbid or find_title depending on the data recieved.

        Returns list of dicts of individual movies from the find_x function.
        '''

        search_term = search_term.replace(" ", "+")

        if search_term[:2] == u'tt' and search_term[2:].isdigit():
            return self.find_imdbid(search_term)
        else:
            return self.find_title(search_term)

    def find_title(self, title):
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
            return 'Search Error.'

    def find_imdbid(self, imdbid):
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
            return 'Search Error.'


class Update(object):

    def __init__(self):
        return

    def update_all(self):
        for movie in self.sql.get_user_movies():
            if movie['rated'] == 'N/A' or int(movie['score']) == 0:
                return


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
