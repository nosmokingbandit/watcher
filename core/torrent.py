import json
import logging
import datetime
import time
import urllib2
import xml.etree.cElementTree as ET
import core
from core.proxy import Proxy


logging = logging.getLogger(__name__)

test_url = u'http://mxq:5060/torrentpotato/thepiratebay?passkey=135fdfdfd895c1ef9ceba603d2dd8ba1&t=movie&imdbid=tt3748528'


class Torrent(object):

    def __init__(self):
        return

    def search_all(self, imdbid):
        torrent_indexers = core.CONFIG['Indexers']['Torrent']

        results = []

        potato_results = self.search_potato(imdbid)
        results = potato_results

        if torrent_indexers['rarbg']:
            rarbg_results = Rarbg.search(imdbid)
            for i in rarbg_results:
                if i not in results:
                    results.append(i)

        return results

    def search_potato(self, imdbid):
        ''' Search all TorrentPotato providers
        imdbid: str imdb id #

        Returns list of dicts with movie info
        '''
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        indexers = core.CONFIG['Indexers']['TorrentPotato'].values()
        results = []

        for indexer in indexers:
            if indexer[2] is False:
                continue
            url = indexer[0]
            if url[-1] == u'/':
                url = url[:-1]
            passkey = indexer[1]

            search_string = u'{}?passkey={}&t=movie&imdbid={}'.format(url, passkey, imdbid)

            logging.info(u'SEARCHING: {}?passkey=PASSKEY&t=movie&imdbid={}'.format(url, imdbid))

            request = urllib2.Request(search_string, headers={'User-Agent': 'Mozilla/5.0'})

            try:
                if proxy_enabled and Proxy.whitelist(url) is True:
                    response = Proxy.bypass(request)
                else:
                    response = urllib2.urlopen(request)

                torrent_results = json.loads(response.read()).get('results')

                if torrent_results:
                    for i in torrent_results:
                        results.append(i)
                else:
                    continue
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e: # noqa
                logging.error(u'Torrent search_potato.', exc_info=True)
                continue

        if results:
            return Torrent.parse_torrent_potato(results)
        else:
            return []

    @staticmethod
    def test_potato_connection(indexer, apikey):
        ''' Tests connection to TorrentPotato API

        '''

        while indexer[-1] == u'/':
            indexer = indexer[:-1]

        response = {}

        url = u'{}?passkey={}'.format(indexer, apikey)

        print url

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            response = urllib2.urlopen(request).read()
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Torrent Potato connection check.', exc_info=True)
            return {'response': 'false', 'message': str(e)}

        try:
            results = json.loads(response)
            if 'results' in results.keys():
                return {'response': True, 'message': 'Connection successful.'}
            else:
                return {'response': False, 'message': 'Malformed json response.'}
        except (SystemExit, KeyboardInterrupt):
            raise
        except ValueError:
            try:
                tree = ET.fromstring(response)
                return {'response': False, 'message': tree.text}
            except Exception, e:
                return {'response': False, 'message': 'Unknown response format.'}
        except Exception, e: # noqa
            logging.error(u'Torrent Potato connection check.', exc_info=True)
            return {'response': 'false', 'message': 'Unknown response format.'}

    @staticmethod
    def parse_torrent_potato(results):
        ''' Sorts and correct keys in results.
        results: list of dicts of results

        Renames, corrects, and adds missing keys

        Returns list of dicts of results
        '''
        item_keep = ('size', 'pubdate', 'title', 'indexer', 'info_link', 'guid', 'torrentfile', 'resolution', 'type', 'seeders')

        for result in results:
            result['size'] = result['size'] * 1024 * 1024
            result['category'] = result['type']
            result['pubdate'] = None
            result['title'] = result['release_name']
            result['indexer'] = result['torrent_id'].split('/')[2]
            result['info_link'] = result['details_url']
            result['torrentfile'] = result['download_url']

            if result['download_url'].startswith('magnet'):
                result['guid'] = result['download_url'].split('&')[0].split(':')[-1]
                result['type'] = 'magnet'
            else:
                result['guid'] = result['download_url']
                result['type'] = 'torrent'

            result['resolution'] = Torrent.get_resolution(result)

            for i in result.keys():
                if i not in item_keep:
                    del result[i]

            result['status'] = u'Available'
            result['score'] = 0
            result['downloadid'] = None

        return results

    @staticmethod
    def get_resolution(result):
        ''' Parses release resolution from newznab category or title.
        :param result: dict of individual search result info

        Helper function for make_item_dict()

        Returns str resolution.
        '''

        title = result['title']
        if '4K' in title or 'UHD' in title or '2160P' in title:
            resolution = u'4K'
        elif '1080' in title:
            resolution = u'1080P'
        elif '720' in title:
            resolution = u'720P'
        elif 'dvd' in title.lower():
            resolution = u'SD'
        else:
            resolution = u'Unknown'
        return resolution


class Rarbg(object):
    '''
    This api is limited to once request every 2 seconds.
    '''

    timeout = None
    token = None

    @staticmethod
    def search(imdbid):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info('Searching Rarbg for {}'.format(imdbid))
        if Rarbg.timeout:
            now = datetime.datetime.now()
            while Rarbg.timeout > now:
                time.sleep(1)
                now = datetime.datetime.now()

        if not Rarbg.token:
            Rarbg.token = Rarbg.get_token()
            if Rarbg.token is None:
                logging.error('Unable to get rarbg token.')
                return []

        url = u'https://torrentapi.org/pubapi_v2.php?token={}&mode=search&search_imdb={}&category=movies&format=json_extended'.format(Rarbg.token, imdbid)

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        Rarbg.timeout = datetime.datetime.now() + datetime.timedelta(seconds=2)
        try:
            if proxy_enabled and Proxy.whitelist('https://torrentapi.org') is True:
                response = Proxy.bypass(request)
            else:
                response = urllib2.urlopen(request)

            response = urllib2.urlopen(request, timeout=60).read()
            response = json.loads(response).get('torrent_results')
            if response:
                results = Rarbg.parse_rarbg(response)
                return results
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Rarbg search.', exc_info=True)
            return []

    @staticmethod
    def get_token():
        url = u'https://torrentapi.org/pubapi_v2.php?get_token=get_token'

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            response = json.loads(urllib2.urlopen(request, timeout=60).read())
            token = response.get('token')
            return token
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Rarbg get_token.', exc_info=True)
            return None

    @staticmethod
    def parse_rarbg(results):
        logging.info('Parsing Rarbg results.')
        item_keep = ('size', 'pubdate', 'title', 'indexer', 'info_link', 'guid', 'torrentfile', 'resolution', 'type', 'seeders')

        for result in results:
            result['indexer'] = 'www.rarbg.to'
            result['info_link'] = result['info_page']
            result['torrentfile'] = result['download']
            result['guid'] = result['download'].split('&')[0].split(':')[-1]
            result['type'] = 'magnet'
            result['pubdate'] = None
            result['category'] = None

            result['resolution'] = Torrent.get_resolution(result)

            for i in result.keys():
                if i not in item_keep:
                    del result[i]

            result['status'] = u'Available'
            result['score'] = 0
            result['downloadid'] = None
        logging.info('Found {} results from Rarbg.'.format(len(results)))
        return results


'''
Required Key:
size, category, pubdate, title, indexer, info_link, guid, torrentfile, resolution, type(magnet, torrent)

'''


'''
{u'torrent_id': u'https://thepiratebay.org/torrent/6744588/Cars_(2006)_720p_BrRip_x264_-_600MB_-_YIFY',
u'seeders': 381
u'freeleech': False,
u'details_url': u'https://thepiratebay.org/torrent/6744588/Cars_(2006)_720p_BrRip_x264_-_600MB_-_YIFY',
u'download_url': u'magnet:?xt=urn:btih:532a821cd3e4a31594b661de2c9e8622546c4655&dn=Cars+%282006%29+720p+BrRip+x264+-+600MB+-+YIFY&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969&tr=udp%3A%2F%2Fzer0day.ch%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fpublic.popcorn-tracker.org%3A6969',
u'imdb_id': u'',
u'leechers': 50,
u'release_name': u'Cars (2006) 720p BrRip x264 - 600MB - YIFY',
u'type': u'movie',
u'size': 601}
'''


'''
{
  "results": [
    {
      "release_name": "John Wick Chapter 2 2017 1080p BluRay AC3 x264--English",
      "torrent_id": "http://www.dnoid.me/files/download/3528456/",
      "details_url": "http://www.dnoid.me/files/details/3528456/9936912/",
      "download_url": "http://mxq:5060/download/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsIjoiaHR0cDovL3d3dy5kbm9pZC5tZS9maWxlcy9kb3dubG9hZC8zNTI4NDU2LyIsIm5iZiI6MTQ4NDU5Mzg0MiwicyI6ImRlbW9ub2lkIn0.l9-9GTbzoASi9G9IRY-IZ_j9d01ySYzLGcu51HW5U6w/John+Wick+Chapter+2+2017+1080p+BluRay+AC3+x264--English.torrent",
      "imdb_id": "",
      "freeleech": false,
      "type": "movie",
      "size": 963,
      "leechers": 0,
      "seeders": 1
    },
    {
      "release_name": "68 latest trailers 2017 720p",
      "torrent_id": "http://www.dnoid.me/files/download/3506006/",
      "details_url": "http://www.dnoid.me/files/details/3506006/9936912/",
      "download_url": "http://mxq:5060/download/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsIjoiaHR0cDovL3d3dy5kbm9pZC5tZS9maWxlcy9kb3dubG9hZC8zNTA2MDA2LyIsIm5iZiI6MTQ4NDU5Mzg0MiwicyI6ImRlbW9ub2lkIn0.KgS2IznzqKCLux2ay8-HUGxkDRdy_kFFv6mD-4DTLKQ/68+latest+trailers+2017+720p.torrent",
      "imdb_id": "",
      "freeleech": false,
      "type": "movie",
      "size": 1401,
      "leechers": 2,
      "seeders": 3
    }
  ],
  "total_results": 2
}

'''
