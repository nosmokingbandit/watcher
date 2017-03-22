import json
import logging
import datetime
import time
import xml.etree.cElementTree as ET
import core
from core.proxy import Proxy
from core.helpers import Url
from core.providers.base import NewzNabProvider


logging = logging.getLogger(__name__)


class Torrent(NewzNabProvider):

    trackers = ['udp://tracker.leechers-paradise.org:6969',
                'udp://zer0day.ch:1337',
                'udp://tracker.coppersurfer.tk:6969',
                'udp://public.popcorn-tracker.org:6969'
                ]

    def __init__(self):
        self.feed_type = 'torrent'
        return

    def search_all(self, imdbid, title, year):
        ''' Search all Torrent indexers.
        imdbid: string imdb movie id.
        title: str movie title
        year: str year of movie release

        Returns list of dicts with sorted nzb information.
        '''

        torz_indexers = core.CONFIG['Indexers']['TorzNab'].values()

        self.imdbid = imdbid

        results = []

        term = '{}+{}'.format(title, year).replace(' ', '+')

        for indexer in torz_indexers:
            if indexer[2] is False:
                continue
            url_base = indexer[0]
            if url_base[-1] != u'/':
                url_base = url_base + '/'
            apikey = indexer[1]

            r = self.search_newznab(url_base, apikey, t='search', cat=2000, q=imdbid)
            for i in r:
                results.append(i)

        torrent_indexers = core.CONFIG['Indexers']['Torrent']

        title = Url.encode(title)
        year = Url.encode(year)

        if torrent_indexers['rarbg']:
            rarbg_results = Rarbg.search(imdbid)
            for i in rarbg_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['limetorrents']:
            lime_results = LimeTorrents.search(imdbid, term)
            for i in lime_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['extratorrent']:
            extra_results = ExtraTorrent.search(imdbid, term)
            for i in extra_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['skytorrents']:
            sky_results = SkyTorrents.search(imdbid, term)
            for i in sky_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['bitsnoop']:
            bit_results = BitSnoop.search(imdbid, term)
            for i in bit_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['torrentz2']:
            torrentz_results = Torrentz2.search(imdbid, term)
            for i in torrentz_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['thepiratebay']:
            tpb_results = ThePirateBay.search(imdbid, term)
            for i in tpb_results:
                if i not in results:
                    results.append(i)

        self.imdbid = None
        return results

    def get_rss(self):
        ''' Gets rss from all torznab providers and individual providers

        Returns list of dicts of latest movies
        '''

        results = []

        results = self._get_rss()

        torrent_indexers = core.CONFIG['Indexers']['Torrent']

        if torrent_indexers['rarbg']:
            rarbg_results = Rarbg.get_rss()
            for i in rarbg_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['limetorrents']:
            lime_results = LimeTorrents.get_rss()
            for i in lime_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['extratorrent']:
            extra_results = ExtraTorrent.get_rss()
            for i in extra_results:
                if i not in results:
                    results.append(i)
        if torrent_indexers['torrentz2']:
            torrentz_results = Torrentz2.get_rss()
            for i in torrentz_results:
                if i not in results:
                    results.append(i)

        return results


class Rarbg(object):
    '''
    This api is limited to once request every 2 seconds.
    '''

    timeout = None
    token = None

    @staticmethod
    def search(imdbid):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Searching Rarbg for {}.'.format(imdbid))
        if Rarbg.timeout:
            now = datetime.datetime.now()
            while Rarbg.timeout > now:
                time.sleep(1)
                now = datetime.datetime.now()

        if not Rarbg.token:
            Rarbg.token = Rarbg.get_token()
            if Rarbg.token is None:
                logging.error(u'Unable to get Rarbg token.')
                return []

        url = u'https://www.torrentapi.org/pubapi_v2.php?token={}&mode=search&search_imdb={}&category=movies&format=json_extended&app_id=Watcher'.format(Rarbg.token, imdbid)

        request = Url.request(url)

        Rarbg.timeout = datetime.datetime.now() + datetime.timedelta(seconds=2)
        try:
            if proxy_enabled and Proxy.whitelist('https://www.torrentapi.org') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

            results = json.loads(response).get('torrent_results')
            if results:
                return Rarbg.parse(results)
            else:
                logging.info(u'Nothing found on Rarbg.')
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Rarbg search failed.', exc_info=True)
            return []

    @staticmethod
    def get_rss():
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Fetching latest RSS from Rarbg.')
        if Rarbg.timeout:
            now = datetime.datetime.now()
            while Rarbg.timeout > now:
                time.sleep(1)
                now = datetime.datetime.now()

        if not Rarbg.token:
            Rarbg.token = Rarbg.get_token()
            if Rarbg.token is None:
                logging.error(u'Unable to get Rarbg token.')
                return []

        url = u'https://www.torrentapi.org/pubapi_v2.php?token={}&mode=list&category=movies&format=json_extended&app_id=Watcher'.format(Rarbg.token)

        request = Url.request(url)

        Rarbg.timeout = datetime.datetime.now() + datetime.timedelta(seconds=2)
        try:
            if proxy_enabled and Proxy.whitelist('https://www.torrentapi.org') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

            results = json.loads(response).get('torrent_results')
            if results:
                return Rarbg.parse(results)
            else:
                logging.info(u'Nothing found in Rarbg RSS.')
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Rarbg RSS fetch failed.', exc_info=True)
            return []

    @staticmethod
    def get_token():
        url = u'https://www.torrentapi.org/pubapi_v2.php?get_token=get_token'

        request = Url.request(url)

        try:
            response = Url.open(request)
            result = json.loads(response)
            token = result.get('token')
            return token
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Failed to get Rarbg token.', exc_info=True)
            return None

    @staticmethod
    def parse(results):
        logging.info(u'Parsing Rarbg results.')
        item_keep = ('size', 'pubdate', 'title', 'indexer', 'info_link', 'guid', 'torrentfile', 'resolution', 'type', 'seeders')

        for result in results:
            result['indexer'] = 'www.rarbg.to'
            result['info_link'] = result['info_page']
            result['torrentfile'] = result['download']
            result['guid'] = result['download'].split('&')[0].split(':')[-1]
            result['type'] = 'magnet'
            result['pubdate'] = None

            for i in result.keys():
                if i not in item_keep:
                    del result[i]

            result['status'] = u'Available'
            result['score'] = 0
            result['downloadid'] = None
        logging.info(u'Found {} results from Rarbg.'.format(len(results)))
        return results


class LimeTorrents(object):

    @staticmethod
    def search(imdbid, term):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Searching LimeTorrents for {}.'.format(term))

        url = u'https://www.limetorrents.cc/searchrss/{}'.format(term)
        request = Url.request(url)

        try:
            if proxy_enabled and Proxy.whitelist('https://www.limetorrents.cc') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

            if response:
                return LimeTorrents.parse(response, imdbid)
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'LimeTorrent search failed.', exc_info=True)
            return []

    @staticmethod
    def get_rss():
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Fetching latest RSS from LimeTorrents.')

        url = u'https://www.limetorrents.cc/rss/16/'
        request = Url.request(url)

        try:
            if proxy_enabled and Proxy.whitelist('https://www.limetorrents.cc') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

            if response:
                return LimeTorrents.parse(response, None)
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'LimeTorrent RSS fetch failed.', exc_info=True)
            return []

    @staticmethod
    def parse(xml, imdbid):
        logging.info(u'Parsing LimeTorrents results.')

        tree = ET.fromstring(xml)

        items = tree[0].findall('item')

        results = []
        for i in items:
            result = {}
            try:
                result['score'] = 0
                result['size'] = int(i.find('size').text)
                result['status'] = u'Available'
                result['pubdate'] = None
                result['title'] = i.find('title').text
                result['imdbid'] = imdbid
                result['indexer'] = 'www.limetorrents.cc'
                result['info_link'] = i.find('comments').text
                result['torrentfile'] = i.find('enclosure').attrib['url']
                result['guid'] = result['torrentfile'].split('.')[1].split('/')[-1].lower()
                result['type'] = 'torrent'
                result['downloadid'] = None

                s = i.find('description').text.split('Seeds: ')[1]
                seed_str = ''
                while s[0].isdigit():
                    seed_str += s[0]
                    s = s[1:]

                result['seeders'] = int(seed_str)

                results.append(result)
            except Exception, e: #noqa
                logging.error(u'Error parsing LimeTorrents XML.', exc_info=True)
                continue

        logging.info(u'Found {} results from LimeTorrents.'.format(len(results)))
        return results


class ExtraTorrent(object):

    @staticmethod
    def search(imdbid, term):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Searching ExtraTorrent for {}.'.format(term))

        url = u'https://www.extratorrent.cc/rss.xml?type=search&cid=4&search={}'.format(term)

        request = Url.request(url)
        try:
            if proxy_enabled and Proxy.whitelist('https://www.extratorrent.cc') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

            if response:
                return ExtraTorrent.parse(response, imdbid)
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'ExtraTorrent search failed.', exc_info=True)
            return []

    @staticmethod
    def get_rss():
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Fetching latest RSS from ExtraTorrent.')

        url = u'https://www.extratorrent.cc/rss.xml?cid=4&type=today'

        request = Url.request(url)
        try:
            if proxy_enabled and Proxy.whitelist('https://www.extratorrent.cc') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

            if response:
                return ExtraTorrent.parse(response, None)
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'ExtraTorrent RSS fetch failed.', exc_info=True)
            return []

    @staticmethod
    def parse(xml, imdbid):
        logging.info(u'Parsing ExtraTorrent results.')

        tree = ET.fromstring(xml)

        items = tree[0].findall('item')

        results = []
        for i in items:
            result = {}
            try:
                result['score'] = 0
                result['size'] = int(i.find('size').text)
                result['status'] = u'Available'
                result['pubdate'] = None
                result['title'] = i.find('title').text
                result['imdbid'] = imdbid
                result['indexer'] = 'www.extratorrent.cc'
                result['info_link'] = i.find('link').text
                result['torrentfile'] = i.find('magnetURI').text
                result['guid'] = result['torrentfile'].split('&')[0].split(':')[-1]
                result['type'] = 'magnet'
                result['downloadid'] = None

                seeders = i.find('seeders').text
                result['seeders'] = 0 if seeders == '---' else seeders

                results.append(result)
            except Exception, e: #noqa
                logging.error(u'Error parsing ExtraTorrent XML.', exc_info=True)
                continue

        logging.info(u'Found {} results from ExtraTorrent.'.format(len(results)))
        return results


class SkyTorrents(object):
    ''' Does not supply rss feed -- backlog searches only. '''

    @staticmethod
    def search(imdbid, term):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Searching SkyTorrents for {}.'.format(term))

        url = u'https://www.skytorrents.in/rss/all/ed/1/{}'.format(term)

        request = Url.request(url)
        try:
            if proxy_enabled and Proxy.whitelist('https://www.skytorrents.in') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

            if response:
                return SkyTorrents.parse(response, imdbid)
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'SkyTorrents search failed.', exc_info=True)
            return []

    @staticmethod
    def parse(xml, imdbid):
        logging.info(u'Parsing SkyTorrents results.')

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

                result['status'] = u'Available'
                result['pubdate'] = None
                result['title'] = i.find('title').text
                result['imdbid'] = imdbid
                result['indexer'] = 'www.skytorrents.in'
                result['info_link'] = i.find('guid').text
                result['torrentfile'] = i.find('link').text
                result['guid'] = result['torrentfile'].split('/')[4]
                result['type'] = 'torrent'
                result['downloadid'] = None

                result['seeders'] = desc[0]

                results.append(result)
            except Exception, e: #noqa
                logging.error(u'Error parsing SkyTorrents XML.', exc_info=True)
                continue

        logging.info(u'Found {} results from SkyTorrents.'.format(len(results)))
        return results


class BitSnoop(object):
    ''' RSS feed doesn't give download links. RSS disabled until I figure it out. '''

    @staticmethod
    def search(imdbid, term):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Searching BitSnoop for {}.'.format(term))

        url = u'https://www.bitsnoop.com/search/video/{}/c/d/1/?fmt=rss'.format(term)

        request = Url.request(url)
        try:
            if proxy_enabled and Proxy.whitelist('https://www.bitsnoop.com') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

                if response:
                    return BitSnoop.parse(response, imdbid)
                else:
                    return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'BitSnoop search failed.', exc_info=True)
            return []

    @staticmethod
    def get_rss():
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Fetching latest RSS from BitSnoop.')

        url = u'https://www.bitsnoop.com/browse/video-movies/?sort=dt_reg&fmt=rss'

        request = Url.request(url)
        try:
            if proxy_enabled and Proxy.whitelist('https://www.bitsnoop.com') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

            if response:
                return BitSnoop.parse(response, None)
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'BitSnoop RSS fetch failed.', exc_info=True)
            return []

    @staticmethod
    def parse(xml, imdbid):
        logging.info(u'Parsing BitSnoop results.')

        tree = ET.fromstring(xml)

        items = tree[0].findall('item')

        results = []
        for i in items:
            result = {}
            try:
                result['score'] = 0
                result['size'] = int(i.find('size').text)
                result['status'] = u'Available'
                result['pubdate'] = None
                result['title'] = i.find('title').text
                result['imdbid'] = imdbid
                result['indexer'] = 'www.bitsnoop.com'
                result['info_link'] = i.find('link').text
                result['torrentfile'] = i.find('{http://xmlns.ezrss.it/0.1/}torrent').find('{http://xmlns.ezrss.it/0.1/}magnetURI').text
                result['guid'] = result['torrentfile'].split('&')[0].split(':')[-1]
                result['type'] = 'magnet'
                result['downloadid'] = None
                result['seeders'] = int(i.find('numSeeders').text)

                results.append(result)
            except Exception, e: #noqa
                logging.error(u'Error parsing BitSnoop XML.', exc_info=True)
                continue

        logging.info(u'Found {} results from BitSnoop.'.format(len(results)))
        return results


class Torrentz2(object):

    @staticmethod
    def search(imdbid, term):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Searching Torrentz2 for {}.'.format(term))

        url = u'https://www.torrentz2.eu/feed?f={}'.format(term)

        request = Url.request(url)
        try:
            if proxy_enabled and Proxy.whitelist('https://www.torrentz2.eu') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

            if response:
                return Torrentz2.parse(response, imdbid)
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Torrentz2 search failed.', exc_info=True)
            return []

    @staticmethod
    def get_rss():
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Fetching latest RSS from Torrentz2.')

        url = u'https://www.torrentz2.eu/feed?f=movies'

        request = Url.request(url)
        try:
            if proxy_enabled and Proxy.whitelist('https://www.torrentz2.eu') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

            if response:
                return Torrentz2.parse(response, None)
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Torrentz2 RSS fetch failed.', exc_info=True)
            return []

    @staticmethod
    def parse(xml, imdbid):
        logging.info(u'Parsing Torrentz2 results.')

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
                result['status'] = u'Available'
                result['pubdate'] = None
                result['title'] = i.find('title').text
                result['imdbid'] = imdbid
                result['indexer'] = 'www.torrentz2.eu'
                result['info_link'] = i.find('link').text
                result['torrentfile'] = u'magnet:?xt=urn:btih:{}&dn={}&tr={}'.format(hsh, result['title'], '&tr='.join(Torrent.trackers))
                result['guid'] = hsh
                result['type'] = 'magnet'
                result['downloadid'] = None
                result['seeders'] = int(desc[4])

                results.append(result)
            except Exception, e: #noqa
                logging.error(u'Error parsing Torrentz2 XML.', exc_info=True)
                continue

        logging.info(u'Found {} results from Torrentz2.'.format(len(results)))
        return results


class ThePirateBay(object):

    @staticmethod
    def search(imdbid, term):
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Searching ThePirateBay for {}.'.format(term))

        url = u'https://www.thepiratebay.org/search/{}/0/99/200'.format(term)

        request = Url.request(url)
        request.add_header('Cookie', 'lw=s')
        try:
            if proxy_enabled and Proxy.whitelist('https://www.thepiratebay.org') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

            if response:
                return ThePirateBay.parse(response, imdbid)
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'ThePirateBay search failed.', exc_info=True)
            return []

    @staticmethod
    def get_rss():
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        logging.info(u'Fetching latest RSS from ThePirateBay.')

        url = u'https://www.thepiratebay.org/browse/201/0/3/0'

        request = Url.request(url)
        try:
            if proxy_enabled and Proxy.whitelist('https://www.thepiratebay.org') is True:
                response = Proxy.bypass(request)
            else:
                response = Url.open(request)

            if response:
                return ThePirateBay.parse(response, None)
            else:
                return []
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'ThePirateBay RSS fetch failed.', exc_info=True)
            return []

    @staticmethod
    def parse(html, imdbid):
        logging.info(u'Parsing ThePirateBay results.')

        html = ' '.join(html.split())
        rows = []
        for i in html.split('<tr>')[1:-1]:
            rows = rows + i.split('<tr class="alt">')

        rows = ['<tr>{}'.format(i.replace('&', '%26')) for i in rows]

        results = []
        for row in rows:
            i = ET.fromstring(row)
            result = {}
            try:

                desc = i[4].text
                m = (1024 ** 3) if desc.split(';')[-1] == 'GiB' else (1024 ** 2)

                size = float(desc.split('%')[0]) * m

                result['score'] = 0
                result['size'] = size
                result['status'] = u'Available'
                result['pubdate'] = None
                result['title'] = i[1][0].text
                result['imdbid'] = imdbid
                result['indexer'] = 'www.thepiratebay.org'
                result['info_link'] = u'https://www.thepiratebay.org{}'.format(i[1][0].attrib['href'])
                result['torrentfile'] = i[3][0][0].attrib['href'].replace('%26', '&')
                result['guid'] = result['torrentfile'].split('&')[0].split(':')[-1]
                result['type'] = 'magnet'
                result['downloadid'] = None
                result['seeders'] = int(i[5].text)

                results.append(result)
            except Exception, e: #noqa
                logging.error(u'Error parsing ThePirateBay XML.', exc_info=True)
                continue

        logging.info(u'Found {} results from ThePirateBay.'.format(len(results)))
        return results
