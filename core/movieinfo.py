import urllib2
import json

import logging
logging = logging.getLogger(__name__)

class Omdb():
    def search(self, search_term ):
        ''' Search OMDB for all matches
        :param search_term: str title of movie to search for.

        For best results pass search_term as "Movie Title 2016"

        Returns list of dicts of individual movies.
        '''

        search_term = search_term.replace(" ", "+")

        search_string = "http://www.omdbapi.com/?type=movie&r=json&s={}".format( search_term )


        request = urllib2.Request( search_string, headers={'User-Agent' : 'Mozilla/5.0'} )

        try:
            results_json = json.load(urllib2.urlopen( request ) )
            if results_json['Response'] == 'False':
                return 'Nothing Found'
            else:
                return results_json['Search'][:6]
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error('OMDB search.', exc_info=True)
            return 'Search Error.'

    def movie_info(self, imdbid):
        ''' Searches OMDB for single movie details.
        :param imdbid: str imdb identification number (tt123456)

        Gives more information than search(), but only for one movie.

        Returns dict.
        '''

        search_string = "http://www.omdbapi.com/?i={}&plot=short&tomatoes=true&r=json".format(imdbid)

        request = urllib2.Request( search_string, headers={'User-Agent' : 'Mozilla/5.0'} )

        try:
            data = json.load(urllib2.urlopen( request ) )
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error('OMDB movie_info.', exc_info=True)

        keep = ('Title', 'Year', 'Released', 'Plot', 'Rated',
                'DVD', 'Poster', 'imdbID', 'tomatoURL', 'tomatoRating')

        for k, v in data.items():
            if k not in keep:
                del data[k]
        data['status'] = 'wanted'

        results_lower = {k.lower(): v for k, v in data.iteritems()}
        return results_lower


class Trailer():
    def get_trailer(self, title_date):
        ''' Gets trailer embed url from Youtube.
        :param title_date: str movie title and date ("Movie Title 2016")

        Attempts to connect 3 times in case Youtube is down or not responding. Can fail.

        Returns str or None
        '''

        search_term = (title_date + 'trailer').replace(' ', '+').encode('utf-8')

        k = 'AIzaSyCOu5KhaS9WcTfNvnRKzzJMf6z-6NGb28M'

        search_string = "https://www.googleapis.com/youtube/v3/search?part=snippet&q={}&maxResults={}&key={}".format(search_term, '1', k)

        request = urllib2.Request( search_string, headers={'User-Agent' : 'Mozilla/5.0'} )

        tries = 0
        while tries < 3:
            try:
                data = urllib2.urlopen(request)
                data = json.load(data)
                return data['items'][0]['id']['videoId']
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e:
                logging.error('Tailer get_trailer.', exc_info=True)
                tries += 1
        return None

