import urllib2
import ssl
import xml.etree.cElementTree as ET
import core
from core import config

import logging
logging = logging.getLogger(__name__)

class NewzNab():

    def __init__(self):
        self.conf = config.Config()

    # Returns a list of results stored as dicts
    def search_all(self, imdbid):
        '''
        Searched every enabled indexer for the supplied imdbid.
        Returns a list of dicts with download information.
        '''
        indexers = core.CONFIG['Indexers'].values()

        self.imdbid = imdbid

        results = []
        imdbid_s = imdbid[2:] #just imdbid numbers

        for indexer in indexers:
            url = indexer[0]
            if url[-1] != '/':
                url = url + '/'
            apikey = indexer[1]

            search_string = '{}api?apikey={}&t=movie&imdbid={}'.format(url, apikey, imdbid_s)

            logging.info('SEARCHING: {}api?apikey=APIKEY&t=movie&imdbid={}'.format(url, imdbid_s))

            request = urllib2.Request( search_string, headers={'User-Agent' : 'Mozilla/5.0'})

            try:
                results_xml = urllib2.urlopen(request).read()
                nn_results = self.parse_newznab_xml(results_xml)
                for result in nn_results:
                    results.append(result)
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e:
                logging.error('NewzNab search_all get xml', exc_info=True)
        return results

    # Returns a list of results in dictionaries. Adds to each dict a key:val of 'indexer':<indexer>
    def parse_newznab_xml(self, feed):
        '''
        Used to parse the xml response from newznab indexers.
        Returns a dictionary of relevant information.
        Some indexers won't return JSON even if you ask nicely, so we have to do this.
        '''

        root = ET.fromstring(feed)

        # This is so ugly, but some newznab sites don't output json. I don't want to include a huge xml parsing module, so here we are. I'm not happy about it either.
        res_list =[]
        for root_child in root:
            if root_child.tag == 'channel':
                for channel_child in root_child:
                    if channel_child.tag == 'title':
                        indexer = channel_child.text
                    if channel_child.tag == 'item':
                        result_item = self.make_item_dict(channel_child)
                        result_item['indexer'] = indexer
                        res_list.append(result_item)
        return res_list

    def make_item_dict(self, item):
        '''
        Helper function for parse_newznab_xml().
        Takes filtered xml and returns dict.
        '''
        item_keep = ('title', 'category', 'link', 'guid', 'size', 'pubDate')
        d = {}
        for ic in item:
            if ic.tag in item_keep:
                d[ic.tag.lower()] = ic.text
            if 'newznab' in ic.tag and ic.attrib['name'] == 'size':
                d['size'] = int(ic.attrib['value'])

        d['resolution'] = self.get_resolution(d)
        d['imdbid'] = self.imdbid
        d['pubdate'] = d['pubdate'][5:16]
        d['type'] = 'nzb'
        d['info_link'] = d['guid']
        d['guid'] = d['link']
        del d['link']
        d['score'] = 0
        d['status'] = 'Available'
        return d

    def get_resolution(self, result):
        '''
        Helper function for parse_newznab_xml().
        Returns str resolution gathered from category or title.
        '''

        title = result['title']
        if result['category'] and 'SD' in result['category']:
            resolution = 'SD'
        elif '4K' in title or 'UHD' in title:
            resolution = '4K'
        elif '1080' in title:
            resolution = '1080P'
        elif '720' in title:
            resolution = '720P'
        else:
            resolution = 'Unknown'
        return resolution
