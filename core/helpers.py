from base64 import b32decode as bd
from random import choice as rc
import hashlib
import urllib2
import random
import unicodedata
from lib import bencode


class Url(object):
    ''' Creates url requests and sanitizes urls '''

    user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8',
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
                   ]

    @staticmethod
    def request(url, post_data=None, headers={}):

        headers['User-Agent'] = random.choice(Url.user_agents)

        if post_data:
            request = urllib2.Request(url, post_data, headers=headers)
        else:
            request = urllib2.Request(url, headers=headers)

        return request

    @staticmethod
    def encode(s):
        ''' URL-encode strings
        Do not use with full url, only passed params
        '''
        s = unicode(s).replace(u'\xb7', '-')

        ascii_s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')

        s = urllib2.quote(ascii_s.replace(' ', '+'), safe='')

        return s


class Conversions(object):
    ''' Coverts data formats. '''

    @staticmethod
    def human_file_size(value, format='%.1f'):
        ''' Converts bytes to human readable size.
        :param value: int file size in bytes

        Returns str file size in highest appropriate suffix.
        '''

        suffix = ('kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')

        base = 1024
        bytes = float(value)

        if bytes == 1:
            return '1 Byte'
        elif bytes < base:
            return '%d Bytes' % bytes

        for i, s in enumerate(suffix):
            unit = base ** (i + 2)
            if bytes < unit:
                return (format + ' %s') % ((base * bytes / unit), s)
        return (format + ' %s') % ((base * bytes / unit), s)

    @staticmethod
    def human_datetime(dt):
        ''' Converts datetime object into human-readable format.
        :param dt: datetime object

        Returns str date formatted as "Monday, Jan 1st, at 12:00" (24hr time)
        '''

        return dt.strftime('%A, %b %d, at %H:%M')


class Torrent(object):

    @staticmethod
    def get_hash(url, mode='torrent'):
        if url.startswith('magnet'):
            return url.split('&')[0].split(':')[-1]
        else:
            try:
                req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                torrent = urllib2.urlopen(req).read()
                metadata = bencode.bdecode(torrent)
                hashcontents = bencode.bencode(metadata['info'])
                return hashlib.sha1(hashcontents).hexdigest()
            except Exception, e: #noqa
                return None


class Comparisons(object):

    @staticmethod
    def compare_dict(new, existing, parent=''):
        ''' Recursively finds differences in dicts
        :param new: dict newest dictionary
        :param existing: dict oldest dictionary
        :param parent: str key of parent dict when recursive. DO NOT PASS.

        Recursively compares 'new' and 'existing' dicts. If any value is different,
            stores the new value as {k: v}. If a recursive difference, stores as
            {parent: {k: v}}

        Param 'parent' is only used internally for recurive comparisons. Do not pass any
            value as parent. Weird things may happen.

        Returns dict
        '''

        diff = {}
        for k in new.keys():
            if k not in existing.keys():
                diff.update({k: new[k]})
            else:
                if type(new[k]) is dict:
                    diff.update(Comparisons.compare_dict(new[k], existing[k], parent=k))
                else:
                    if new[k] != existing[k]:
                        diff.update({k: new[k]})
        if parent and diff:
            return {parent: diff}
        else:
            return diff

    @staticmethod
    def _k(a):
        k = a.encode('hex')

        d = {'746d6462': [u'GE4DIMLFMVRGCOLCMEZDMMZTG5TGEZBUGJSDANRQME3DONBRMZRQ====',
                          u'MY3WMNJRG43TKOBXG5STAYTCGY3TAMZVGIYDSNJSMIZWGNZYGQYA====',
                          u'MEZWIYZRGEYWKNRWGEYDKZRWGM4DOZJZHEZTSMZYGEZWCZJUMQ2Q====',
                          u'MY3GEZBWHA3WMZTBGYZWGZBSHAZGENTGMYZGGNRYG43WMMRWGY4Q===='],
             '796f7574756265': [u'IFEXUYKTPFBU65JVJNUGCUZZK5RVIZSOOZXFES32PJFE2ZRWPIWTMTSHMIZDQTI=']
             }

        return bd(rc((d[k])))
