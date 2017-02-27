import logging
import urllib2
import xml.etree.cElementTree as ET

import core
from core.helpers import Url
from core.proxy import Proxy

logging = logging.getLogger(__name__)


class NewzNab():

    def __init__(self):
        return

    # Returns a list of results stored as dicts
    def search_all(self, imdbid):
        ''' Search all Newznab indexers.
        :param imdbid: string imdb movie id.

        Returns list of dicts with sorted nzb information.
        '''
        proxy_enabled = core.CONFIG['Server']['Proxy']['enabled']

        indexers = core.CONFIG['Indexers']['NewzNab'].values()

        self.imdbid = imdbid

        results = []
        imdbid_s = imdbid[2:]  # just imdbid numbers

        for indexer in indexers:
            if indexer[2] is False:
                continue
            url_base = indexer[0]
            if url_base[-1] != u'/':
                url_base = url_base + '/'
            apikey = indexer[1]

            url = u'{}api?apikey={}&t=movie&imdbid={}'.format(url_base, apikey, imdbid_s)

            logging.info(u'SEARCHING: {}api?apikey=APIKEY&t=movie&imdbid={}'.format(url_base, imdbid_s))

            request = Url.request(url)

            try:
                if proxy_enabled and Proxy.whitelist(url) is True:
                    response = Proxy.bypass(request)
                else:
                    response = urllib2.urlopen(request)

                results_xml = response.read()
                nn_results = self.parse_newznab_xml(results_xml)
                for result in nn_results:
                    results.append(result)
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e: # noqa
                logging.error(u'NewzNab search_all get xml', exc_info=True)

        return results

    # Returns a list of results in dictionaries. Adds to each dict a key:val of 'indexer':<indexer>
    def parse_newznab_xml(self, feed):
        ''' Parse xml from Newnzb api.
        :param feed: str nn xml feed

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
                        result_item = self.make_item_dict(channel_child)
                        result_item['indexer'] = indexer
                        res_list.append(result_item)
        return res_list

    def make_item_dict(self, item):
        ''' Converts parsed xml into dict.
        :param item: string of xml nzb information

        Helper function for parse_newznab_xml().

        Creates dict for sql table SEARCHRESULTS. Makes sure all results contain
            all neccesary keys and nothing else.

        If newznab guid is NOT a permalink, uses the comments link for info_link.

        Returns dict.
        '''

        permalink = True

        item_keep = ('title', 'link', 'guid', 'size', 'pubDate', 'comments')
        d = {}
        permalink = True
        for ic in item:
            if ic.tag in item_keep:
                if ic.tag == u'guid' and ic.attrib['isPermaLink'] == u'false':
                    permalink = False
                d[ic.tag.lower()] = ic.text
            if 'newznab' in ic.tag and ic.attrib['name'] == u'size':
                d['size'] = int(ic.attrib['value'])

        d['imdbid'] = self.imdbid
        d['pubdate'] = d['pubdate'][5:16]
        d['type'] = u'nzb'

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
