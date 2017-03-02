import xml.etree.cElementTree as ET
import urllib2
import logging

import core
from core.helpers import Url
from core.proxy import Proxy


class NewzNabProvider(object):
    '''
    Base class for NewzNab and TorzNab providers.
    Methods:
        search_newznab      searches indexer for imdbid
        parse_newznab_xml   parses newznab-formatted xml into dictionary
        test_connection     static_method to test connetion and apikey

    Required imports:
        import xml.etree.cElementTree as ET
        import urllib2
        from core.helpers import Url
        from core.proxy import Proxy
        from core.providers.base import NewzNabProvider

    '''

    def search_newznab(self, url_base, apikey, imdbid=None, term=None):
        ''' Searches Newznab for imdbid
        url_base: str base url for all requests (https://indexer.com/)
        apikey: str api key for indexer
        imdbid: str imdbid *numbers only* ie 0055447    <optional*>
        term: str title and year of movie to search     <optional*>

        *Either imdbid or term MUST be passed.
        Pass term for torznab searches, imdbid for newznab searches.

        Returns list of dicts of search results
        '''

        if not imdbid and not term:
            logging.warning('Neither imdbid or term supplied to search.')
            return []
        elif imdbid:
            url = u'{}api?apikey={}&t=movie&imdbid={}'.format(url_base, apikey, imdbid)
            logging.info(u'SEARCHING: {}api?apikey=APIKEY&t=movie&imdbid={}'.format(url_base, imdbid))
        elif term:
            term = Url.encode(term.replace(' ', '+'))
            url = u'{}api?apikey={}&t=search&cat=2000&q={}'.format(url_base, apikey, term)
            logging.info(u'SEARCHING: {}api?apikey=APIKEY&t=search&cat=2000&q={}'.format(url_base, term))

        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        request = Url.request(url)

        try:
            if proxy_enabled and Proxy.whitelist(url) is True:
                response = Proxy.bypass(request)
            else:
                response = urllib2.urlopen(request)

            results_xml = response.read()
            return self.parse_newznab_xml(results_xml)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Newz/TorzNab backlog search', exc_info=True)
            return []

    def _get_rss(self):
        ''' Get latest uploads from all indexers

        Returns list of dicts with parsed nzb info
        '''

        self.imdbid = None

        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        if self.feed_type == 'nzb':
            indexers = core.CONFIG['Indexers']['NewzNab'].values()
        else:
            indexers = core.CONFIG['Indexers']['TorzNab'].values()

        results = []

        for indexer in indexers:
            if indexer[2] is False:
                continue
            url_base = indexer[0]
            if url_base[-1] != u'/':
                url_base = url_base + '/'
            apikey = indexer[1]

            url = u'{}api?t=movie&cat=2000&extended=1&offset=0&apikey={}'.format(url_base, apikey)

            logging.info(u'RSS_SYNC: {}api?t=movie&cat=2000&extended=1&offset=0&apikey=APIKEY'.format(url_base))

            request = Url.request(url)

            try:
                if proxy_enabled and Proxy.whitelist(url) is True:
                    response = Proxy.bypass(request)
                else:
                    response = urllib2.urlopen(request)

                results_xml = response.read()
                return self.parse_newznab_xml(results_xml)
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e: # noqa
                logging.error(u'Newz/TorzNab rss get xml.', exc_info=True)

        return results

    # Returns a list of results in dictionaries. Adds to each dict a key:val of 'indexer':<indexer>
    def parse_newznab_xml(self, feed):
        ''' Parse xml from Newnzb api.
        :param feed: str nn xml feed
        kind: str type of feed we are parsing, either nzb or torrent

        Returns dict of sorted nzb information.
        '''

        root = ET.fromstring(feed)
        indexer = u''
        # This is so ugly, but some newznab sites don't output json. I don't want to include a huge xml parsing module, so here we are. I'm not happy about it either.
        res_list = []
        for root_child in root:
            if root_child.tag == u'channel':
                for channel_child in root_child:
                    if channel_child.tag == u'title':
                        indexer = channel_child.text
                    if not indexer and channel_child.tag == u'link':
                        indexer = channel_child.text
                    if channel_child.tag == u'item':
                        result_item = self._make_item_dict(channel_child)
                        result_item['indexer'] = indexer
                        res_list.append(result_item)
        return res_list

    def _make_item_dict(self, item):
        ''' Converts parsed xml into dict.
        :param item: string of xml nzb information
        kind: str 'nzb' or 'torrent' depending on type of feed

        Helper function for parse_newznab_xml().

        Creates dict for sql table SEARCHRESULTS. Makes sure all results contain
            all neccesary keys and nothing else.

        If newznab guid is NOT a permalink, uses the comments link for info_link.

        Gets torrent hash and determines if download is torrent file or magnet uri.

        Returns dict.
        '''

        item_keep = ('title', 'link', 'guid', 'size', 'pubDate', 'comments')
        d = {}
        permalink = True
        for ic in item:
            if ic.tag in item_keep:
                if ic.tag == u'guid' and ic.attrib.get('isPermaLink', 'false') == u'false':
                    permalink = False
                d[ic.tag.lower()] = ic.text
            if not d.get('size') and ('newznab' in ic.tag or 'torznab' in ic.tag) and ic.attrib['name'] == u'size':
                d['size'] = ic.attrib['value']
            if 'torznab' in ic.tag and ic.attrib['name'] == 'seeders':
                d['seeders'] = int(ic.attrib['value'])
            if 'newznab' in ic.tag and ic.attrib['name'] == u'imdb':
                d['imdbid'] = 'tt{}'.format(ic.attrib['value'])

        d['size'] = int(d['size'])
        if not d.get('imdbid'):
            d['imdbid'] = self.imdbid
        d['pubdate'] = d['pubdate'][5:16]

        if not permalink:
            d['info_link'] = d['comments']
        else:
            d['info_link'] = d['guid']

        del d['comments']
        d['guid'] = d['link']
        del d['link']
        d['score'] = 0
        d['status'] = u'Available'
        d['torrentfile'] = None
        d['downloadid'] = None

        if self.feed_type == 'nzb':
            d['type'] = u'nzb'
        else:
            d['torrentfile'] = d['guid']
            if d['guid'].startswith('magnet'):
                d['guid'] = d['guid'].split('&')[0].split(':')[-1]
                d['type'] = 'magnet'
            else:
                d['type'] = 'torrent'

        return d

    @staticmethod
    def test_connection(indexer, apikey):
        ''' Tests connection to NewzNab API

        '''

        if not indexer:
            return {'response': False, 'error': 'Indexer field is blank.'}

        while indexer[-1] == '/':
            indexer = indexer[:-1]

        response = {}

        logging.info(u'Testing connection to {}'.format(indexer))

        url = u'{}/api?apikey={}&t=search&id=tt0063350'.format(indexer, apikey)

        request = Url.request(url)
        try:
            response = urllib2.urlopen(request).read()
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'NewzNab connection check.', exc_info=True)
            return {'response': False, 'message': 'No connection could be made because the target machine actively refused it.'}

        if '<error code="' in response:
            error = ET.fromstring(response)
            if error.attrib['description'] == 'Missing parameter':
                return {'response': True, 'message': 'Connection successful.'}
            else:
                return {'response': False, 'message': error.attrib['description']}
        elif 'unauthorized' in response.lower():
            return {'response': False, 'message': 'Incorrect API key.'}
        else:
            return {'response': True, 'message': 'Connection successful.'}
