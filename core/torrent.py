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

    trackers = ['udp://tracker.leechers-paradise.org:6969',
                'udp://zer0day.ch:1337',
                'udp://tracker.coppersurfer.tk:6969',
                'udp://public.popcorn-tracker.org:6969'
                ]

    def __init__(self):
        return

    def search_all(self, imdbid, title, year):
        torrent_indexers = core.CONFIG['Indexers']['Torrent']

        results = []

        potato_results = self.search_potato(imdbid)
        results = potato_results

        if torrent_indexers['rarbg']:
            rarbg_results = Rarbg.search(imdbid)
            for i in rarbg_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['limetorrents']:
            lime_results = LimeTorrents.search(imdbid, title, year)
            for i in lime_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['extratorrent']:
            extra_results = ExtraTorrent.search(imdbid, title, year)
            for i in extra_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['skytorrents']:
            sky_results = SkyTorrents.search(imdbid, title, year)
            for i in sky_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['bitsnoop']:
            bit_results = BitSnoop.search(imdbid, title, year)
            for i in bit_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['torrentz2']:
            torrentz_results = Torrentz2.search(imdbid, title, year)
            for i in torrentz_results:
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
                results = Rarbg.parse(response)
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
    def parse(results):
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


class LimeTorrents(object):

    @staticmethod
    def search(imdbid, title, year):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info('Searching LimeTorrents for {}'.format(title))
        url = u'https://www.limetorrents.cc/searchrss/{}+{}'.format(title, year).replace(' ', '+')

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            if proxy_enabled and Proxy.whitelist('https://www.limetorrents.cc') is True:
                response = Proxy.bypass(request)
            else:
                response = urllib2.urlopen(request)

            response = urllib2.urlopen(request, timeout=60).read()
            if response:
                results = LimeTorrents.parse(response, imdbid)
                return results
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'LimeTorrent search.', exc_info=True)
            return []

    @staticmethod
    def parse(xml, imdbid):
        logging.info('Parsing LimeTorrents results.')

        tree = ET.fromstring(xml)

        items = tree[0].findall('item')

        results = []
        for i in items:
            result = {}
            try:
                result['score'] = 0
                result['size'] = int(i.find('size').text)
                result['category'] = i.find('category').text
                result['status'] = u'Available'
                result['pubdate'] = None
                result['title'] = i.find('title').text
                result['imdbid'] = imdbid
                result['indexer'] = 'www.limetorrents.cc'
                result['info_link'] = i.find('comments').text
                result['torrentfile'] = i.find('enclosure').attrib['url']
                result['guid'] = result['torrentfile'].split('.')[1].split('/')[-1].lower()
                result['resolution'] = Torrent.get_resolution(result)
                result['type'] = 'torrent'
                result['downloadid'] = None

                result['seeders'] = i.find('description').text.split(' ')[1]

                results.append(result)
            except Exception, e: #noqa
                logging.error('Error parsing LimeTorrents XML.', exc_info=True)
                continue

        logging.info('Found {} results from LimeTorrents.'.format(len(results)))
        return results


class ExtraTorrent(object):

    @staticmethod
    def search(imdbid, title, year):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info('Searching ExtraTorrent for {}'.format(title))

        url = u'https://extratorrent.cc/rss.xml?type=search&cid=4&search={}+{}'.format(title, year).replace(' ', '+')

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            if proxy_enabled and Proxy.whitelist('https://www.limetorrents.cc') is True:
                response = Proxy.bypass(request)
            else:
                response = urllib2.urlopen(request)

            response = urllib2.urlopen(request, timeout=60).read()
            if response:
                results = ExtraTorrent.parse(response, imdbid)
                return results
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'ExtraTorrent search.', exc_info=True)
            return []

    @staticmethod
    def parse(xml, imdbid):
        logging.info('Parsing ExtraTorrent results.')

        tree = ET.fromstring(xml)

        items = tree[0].findall('item')

        results = []
        for i in items:
            result = {}
            try:
                result['score'] = 0
                result['size'] = int(i.find('size').text)
                result['category'] = i.find('category').text
                result['status'] = u'Available'
                result['pubdate'] = None
                result['title'] = i.find('title').text
                result['imdbid'] = imdbid
                result['indexer'] = 'www.extratorrent.cc'
                result['info_link'] = i.find('link').text
                result['torrentfile'] = i.find('magnetURI').text
                result['guid'] = result['torrentfile'].split('&')[0].split(':')[-1]
                result['resolution'] = Torrent.get_resolution(result)
                result['type'] = 'magnet'
                result['downloadid'] = None

                seeders = i.find('seeders').text
                result['seeders'] = 0 if seeders == '---' else seeders

                results.append(result)
            except Exception, e: #noqa
                logging.error('Error parsing ExtraTorrent XML.', exc_info=True)
                continue

        logging.info('Found {} results from ExtraTorrent.'.format(len(results)))
        return results


class SkyTorrents(object):

    @staticmethod
    def search(imdbid, title, year):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info('Searching SkyTorrents for {}'.format(title))

        url = u'https://www.skytorrents.in/rss/all/ed/1/{}+{}'.format(title, year).replace(' ', '+')

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            if proxy_enabled and Proxy.whitelist('https://www.skytorrents.in') is True:
                response = Proxy.bypass(request)
            else:
                response = urllib2.urlopen(request)

            response = urllib2.urlopen(request, timeout=60).read()
            if response:
                results = SkyTorrents.parse(response, imdbid)
                return results
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'SkyTorrents search.', exc_info=True)
            return []

    @staticmethod
    def parse(xml, imdbid):
        logging.info('Parsing SkyTorrents results.')

        tree = ET.fromstring(xml)

        items = tree[0].findall('item')

        results = []
        for i in items:
            result = {}
            try:
                result['score'] = 0

                desc = i.find('description').text.split(' ')

                m = (1024 ** 2) if desc[-2] == 'MB' else (1024 ** 3)
                result['size'] = int(float(desc[-3]) * m)

                result['category'] = i.find('category').text
                result['status'] = u'Available'
                result['pubdate'] = None
                result['title'] = i.find('title').text
                result['imdbid'] = imdbid
                result['indexer'] = 'www.skytorrents.in'
                result['info_link'] = i.find('guid').text
                result['torrentfile'] = i.find('link').text
                result['guid'] = result['torrentfile'].split('/')[4]
                result['resolution'] = Torrent.get_resolution(result)
                result['type'] = 'torrent'
                result['downloadid'] = None

                result['seeders'] = desc[0]

                results.append(result)
            except Exception, e: #noqa
                logging.error('Error parsing SkyTorrents XML.', exc_info=True)
                continue

        logging.info('Found {} results from SkyTorrents.'.format(len(results)))
        return results


class BitSnoop(object):

    @staticmethod
    def search(imdbid, title, year):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info('Searching BitSnoop for {}'.format(title))

        url = u'https://bitsnoop.com/search/video/{}+{}/c/d/1/?fmt=rss'.format(title, year).replace(' ', '+')

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            if proxy_enabled and Proxy.whitelist('https://bitsnoop.com') is True:
                response = Proxy.bypass(request)
            else:
                response = urllib2.urlopen(request)

            response = urllib2.urlopen(request, timeout=60).read()
            if response:
                results = BitSnoop.parse(response, imdbid)
                return results
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'BitSnoop search.', exc_info=True)
            return []

    @staticmethod
    def parse(xml, imdbid):
        logging.info('Parsing BitSnoop results.')

        tree = ET.fromstring(xml)

        items = tree[0].findall('item')

        results = []
        for i in items:
            result = {}
            try:
                result['score'] = 0
                result['size'] = int(i.find('size').text)
                result['category'] = i.find('category').text.replace(u'\xbb', '>')
                result['status'] = u'Available'
                result['pubdate'] = None
                result['title'] = i.find('title').text
                result['imdbid'] = imdbid
                result['indexer'] = 'www.bitsnoop.com'
                result['info_link'] = i.find('link').text
                result['torrentfile'] = i.find('{http://xmlns.ezrss.it/0.1/}torrent').find('{http://xmlns.ezrss.it/0.1/}magnetURI').text
                result['guid'] = result['torrentfile'].split('&')[0].split(':')[-1]
                result['resolution'] = Torrent.get_resolution(result)
                result['type'] = 'magnet'
                result['downloadid'] = None
                result['seeders'] = int(i.find('numSeeders').text)

                results.append(result)
            except Exception, e: #noqa
                logging.error('Error parsing BitSnoop XML.', exc_info=True)
                continue

        logging.info('Found {} results from BitSnoop.'.format(len(results)))
        return results


class Torrentz2(object):

    @staticmethod
    def search(imdbid, title, year):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info('Searching Torrentz2 for {}'.format(title))

        url = u'https://torrentz2.eu/feed?f={}+{}'.format(title, year).replace(' ', '+')

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            if proxy_enabled and Proxy.whitelist('https://torrentz2.eu') is True:
                response = Proxy.bypass(request)
            else:
                response = urllib2.urlopen(request)

            response = urllib2.urlopen(request, timeout=60).read()
            if response:
                results = Torrentz2.parse(response, imdbid)
                return results
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Torrentz2 search.', exc_info=True)
            return []

    @staticmethod
    def parse(xml, imdbid):
        logging.info('Parsing Torrentz2 results.')

        tree = ET.fromstring(xml)

        items = tree[0].findall('item')

        results = []
        for i in items:
            result = {}
            try:
                desc = i.find('description').text.split(' ')
                hsh = desc[-1]

                m = (1024 ** 2) if desc[2] == 'MB' else (1024 ** 3)

                result['score'] = 0
                result['size'] = int(desc[1]) * m
                result['category'] = i.find('category').text
                result['status'] = u'Available'
                result['pubdate'] = None
                result['title'] = i.find('title').text
                result['imdbid'] = imdbid
                result['indexer'] = 'www.torrentz2.eu'
                result['info_link'] = i.find('link').text
                result['torrentfile'] = u'magnet:?xt=urn:btih:{}&dn={}&tr={}'.format(hsh, result['title'], '&tr='.join(Torrent.trackers))
                result['guid'] = hsh
                result['resolution'] = Torrent.get_resolution(result)
                result['type'] = 'magnet'
                result['downloadid'] = None
                result['seeders'] = int(desc[4])

                results.append(result)
            except Exception, e: #noqa
                logging.error('Error parsing Torrentz2 XML.', exc_info=True)
                continue

        logging.info('Found {} results from Torrentz2.'.format(len(results)))
        return results
