import os

from hachoir_parser import createParser
from hachoir_metadata import extractMetadata
from core.movieinfo import TMDB
from core import sqldb
import PTN
import datetime
import logging

logging = logging.getLogger(__name__)


class ImportDirectory(object):

    def __init__(self):
        self.tmdb = TMDB()
        self.sql = sqldb.SQL()
        return

    def scan_dir(self, directory, minsize=500, recursive=True):
        ''' Scans directory for movie files
        directory: str base directory of movie library
        minsize: int minimum filesize in MB <default 500>
        recursive: bool scan recusrively or just root directory <default True>

        Returns list of dicts of movie info
        '''

        logging.info('Scanning {} for movies.'.format(directory))

        files = []
        if recursive:
            for root, dirs, filenames in os.walk(directory):
                for f in filenames:
                    files.append(os.path.join(root, f))
        else:
            files = [os.path.join(directory, i) for i in os.listdir(directory) if os.path.isfile(os.path.join(directory, i))]

        files = [unicode(i) for i in files if os.path.getsize(i) >= (minsize * 1024**2)]

        movies = {}
        for i in files:
            size = os.path.getsize(i)
            if size < (minsize * 1024**2):
                continue

            movies[i] = self.get_metadata(i)
            movies[i]['size'] = size

        return movies

    def get_metadata(self, filepath):
        ''' Gets video metadata using hachoir_parser
        filepath: str absolute path to movie file

        On failure, can return empty dict

        Returns dict
        '''

        logging.info('Gathering metada for {}.'.format(filepath))

        data = {
            'title': '',
            'year': '',
            'resolution': '',
            'releasegroup': '',
            'audiocodec': '',
            'videocodec': '',
            'source': '',
            'imdbid': '',
            'size': ''
            }

        titledata = PTN.parse(os.path.basename(filepath))
        # this key is useless
        titledata.pop('excess', None)
        # Make sure this matches our key names
        if 'codec' in titledata:
            titledata['videocodec'] = titledata.pop('codec')
        if 'audio' in titledata:
            titledata['audiocodec'] = titledata.pop('audio')
        if 'quality' in titledata:
            titledata['source'] = titledata.pop('quality')
        if 'group' in titledata:
            titledata['releasegroup'] = titledata.pop('group')
        if 'resolution' in titledata:
            titledata['resolution'] = titledata['resolution'].upper()

        data.update(titledata)

        metadata = None
        try:
            parser = createParser(filepath)
            extractor = extractMetadata(parser)
            metadata = extractor.exportDictionary(human=False)
            parser.stream._input.close()
            data.update(metadata)

        except Exception, e: #noqa
            logging.warning('Unable to parse metadata.', exc_info=True)

        if metadata and not data['resolution']:
            if metadata.get('Metadata'):
                width = metadata['Metadata'].get('width')
            elif metadata.get('video[1]'):
                width = metadata['video[1]'].get('width')

            if width:
                width = int(width)
                if width > 1920:
                    data['resolution'] = '4K'
                elif 1920 >= width > 1440:
                    data['resolution'] = '1080P'
                elif 1440 >= width > 720:
                    data['resolution'] = '720P'
                else:
                    data['resolution'] = 'SD'

        if metadata and not data['audiocodec']:
            if metadata.get('audio[1]'):
                data['audiocodec'] = metadata['audio[1]'].get('compression').replace('A_', '')
        if metadata and not data['videocodec']:
            if metadata.get('video[1]'):
                data['videocodec'] = metadata['video[1]'].get('compression').split('/')[0].replace('V_', '')

        if data.get('title') and not data.get('imdbid'):
            data['imdbid'] = self.tmdb.get_imdbid(title=data['title'], year=data.get('year', ''))

        if data['imdbid']:
            tmdbdata = self.tmdb.search(data['imdbid'], single=True)
            data['year'] = tmdbdata['release_date'][:4]
            data.update(tmdbdata)

        else:
            logging.warning('Unable to find imdbid.')

        return data

    def fake_search_result(self, movie):
        ''' Generated fake search result for imported movies
        movie: dict of movie info

        Resturns dict to match SEARCHRESULTS table
        '''

        result = {'category': 'Movie',
                  'status': 'Finished',
                  'info_link': '#',
                  'pubdate': None,
                  'title': None,
                  'imdbid': movie['imdbid'],
                  'torrentfile': None,
                  'indexer': 'Library Import',
                  'date_found': str(datetime.date.today()),
                  'score': None,
                  'type': 'import',
                  'downloadid': None,
                  'guid': None,
                  'resolution': movie.get('resolution'),
                  'size': movie.get('size', '')
                  }

        title = '{}.{}.{}.{}.{}.{}.{}'.format(movie['title'],
                                              movie['year'],
                                              result['resolution'],
                                              movie['source'],
                                              movie['audiocodec'],
                                              movie['videocodec'],
                                              movie['releasegroup']
                                              )

        print title

        while title[-1] == '.':
            title = title[:-1]

        while '..' in title:
            title = title.replace('..', '.')

        print title

        result['title'] = title

        result['guid'] = 'IMPORT{}'.format(title.encode("hex").zfill(16)[:16])

        return result
