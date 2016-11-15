from core import config
from fuzzywuzzy import fuzz, process
from datetime import datetime, timedelta

import logging
logging = logging.getLogger(__name__)

class ScoreResults():

    def __init__(self):
        return

    # returns list of dictionary results after filtering and scoring
    def score(self, results, title, type):
        self.results = results
        c = config.Config()
        filters = c['Filters']
        qualities = c['Quality']
        retention = int(c['Search']['retention'])
        required = filters['requiredwords'].lower().split(',')
        preferred = filters['preferredwords'].lower().split(',')
        ignored = filters['ignoredwords'].lower().split(',')
        today = datetime.today()

        # These all just modify self.results
        self.remove_ignored(ignored)
        self.keep_required(required)
        self.retention_check(retention, today)
        self.score_quality(qualities)
        self.fuzzy_title(title)
        self.score_preferred(preferred)



        return self.results

    def remove_ignored(self, words):
        if words[0] == '':
            return
        for word in words:
            self.results = [r for r in self.results if word not in r['title'].lower()]

    def keep_required(self, words):
        if words[0] == '':
            return
        for word in words:
            self.results = [r for r in self.results if word in r['title'].lower()]

    def retention_check(self, retention, today):
        if retention == 0:
            return
        l = []
        for result in self.results:
            if result['type'] != 'nzb':
                l.append(result)
            else:
                pubdate = datetime.strptime(result['pubdate'], '%d %b %Y')
                age = (today - pubdate).days
                if age < retention:
                    l.append(result)
        self.results = l

    def score_preferred(self, words):
        if words[0] == '':
            return
        for word in words:
            for result in self.results:
                if word in result['title'].lower():
                    result['score'] += 10

    def fuzzy_title(self, title):
        l = []
        for result in self.results:
            title = title.replace(' ', '.').replace(':', '.').lower()
            test = result['title'].replace(' ', '.').lower()
            match = fuzz.partial_ratio(title, test)
            if match > 50:
                result['score'] += (match / 20)
                l.append(result)
        self.results = l

    def score_quality(self, qualities):
        l = []
        for result in self.results:
            resolution = result['resolution']
            size = result['size'] / 1000000
            for qi in qualities:
                ql = qualities[qi].split(',')
                if ql[0] != 'true':
                    continue
                priority = int(ql[1])
                min_size = int(ql[2])
                max_size = int(ql[3])

                if resolution == qi:
                    if min_size < size < max_size:
                        result['score'] += (8 - priority)*100
                        l.append(result)
        self.results = l

"""
SCORING COLUMNS. I swear some day this will make sense.

4321

<4>
0-4
Resolution Match. Starts at 8.
Remove 1 point for the priority of the matched resolution.
So if we want 1080P then 720P in that order, 1080 movies will get 0 points removed, where 720P will get 1 point removed.
We do this because the jquery sortable gives higher priority items a lower number, so 0 is the most important item. This allows a large amount of preferred word matches to overtake a resolution match.

<3-1>
0-100
Add 10 points for every preferred word match.

"""


"""
JUST DESCRIPTIONS

boost.3d.2016.720p.bluray.x264-value
    How To Train Your Dragon 1 Nederlands 2010 Dutch XviD
    How To Train Your Dragon 1 2010 English XviD
How.To.Train.Your.Dragon.3D.2010.1080p.BluRay.Half.OU.DTS.x264-HDMaNiAcS-sample
How.To.Train.Your.Dragon.3D.2010.1080p.BluRay.Half.OU.DTS.x264-HDMaNiAcS
How.to.Train.Your.Dragon.2010.Blu-ray.EUR.1080p.AVC.DD5.1-HDCLUB
How.to.Train.Your.Dragon.2010.1080p.Bluray.DTS.x264-SHiTSoNy
How.to.Train.Your.Dragon.2010.1080p.Bluray.DTS.x264-SHiTSoNy
    How To Train Your Dragon (2010) 1080P BluRay AAC2.0 X264
    How To Train Your Dragon (2010) 1080P BluRay AAC2.0 X264
    How To Train Your Dragon (2010) 1080P BluRay AAC2.0 X264
    How To Train Your Dragon (2010) 1080P BluRay AAC2.0 X264
    Dragons.2010.FR.DVDRip.Xvid.boheme
    How.To.Train.Your.Dragon.2010.DVDSCR.XviD-ViSiON
    How.To.Train.Your.Dragon.2010.SUBFIX.DVDRip.XviD-TASTE
    How.To.Train.Your.Dragon.2010.DVDRip.XviD-TASTE
How.to.Train.Your.Dragon.DVDR-Replica
    How.To.Train.Your.Dragon.2010.DUTCH.BDRip.XviD-DiXi
How.To.Train.Your.Dragon.2010.iNTERNAL.BDRip.x264-EXViDiNT
How.To.Train.Your.Dragon.2010.iNTERNAL.BDRip.x264-EXViDiNT
    How.To.Train.Your.Dragon.2010.DVDRip.XviD-TASTE

"""

"""
Example DATA:
[   {   'category': 'Movie > SD',
        'comments': 'https://6box.me/details/a0a215e5cea058e177e2b4c257d9c3f6#comments',
        'description': 'war dogs 2016 hd-ts x264-cpg',
        'guid': 'https://6box.me/details/a0a215e5cea058e177e2b4c257d9c3f6',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/a0a215e5cea058e177e2b4c257d9c3f6.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2030',
                            'guid': 'a0a215e5cea058e177e2b4c257d9c3f6',
                            'size': '2589310900'},
        'pubDate': 'Fri, 26 Aug 2016 23:24:44 -0400',
        'title': 'war dogs 2016 hd-ts x264-cpg'},

    {   'category': 'Movie > HD',
        'comments': 'https://6box.me/details/eeb541d8c64f544ce9a32f4a24efdbce#comments',
        'description': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv',
        'guid': 'https://6box.me/details/eeb541d8c64f544ce9a32f4a24efdbce',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/eeb541d8c64f544ce9a32f4a24efdbce.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2040',
                            'guid': 'eeb541d8c64f544ce9a32f4a24efdbce',
                            'size': '870957781'},
        'pubDate': 'Fri, 26 Aug 2016 21:41:44 -0400',
        'title': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv'},

    {   'category': 'Movie > HD',
        'comments': 'https://6box.me/details/3e6a50bdf2f0e897dd39aa7aa9196d77#comments',
        'description': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv',
        'guid': 'https://6box.me/details/3e6a50bdf2f0e897dd39aa7aa9196d77',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/3e6a50bdf2f0e897dd39aa7aa9196d77.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2040',
                            'guid': '3e6a50bdf2f0e897dd39aa7aa9196d77',
                            'size': '870956706'},
        'pubDate': 'Fri, 26 Aug 2016 21:41:43 -0400',
        'title': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv'},

    {   'category': 'Movie > SD',
        'comments': 'https://6box.me/details/0e820dde0ad4260256b4f0faf7df114a#comments',
        'description': 'War Dogs 2016 HD-TS x264-CPG',
        'guid': 'https://6box.me/details/0e820dde0ad4260256b4f0faf7df114a',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/0e820dde0ad4260256b4f0faf7df114a.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2030',
                            'guid': '0e820dde0ad4260256b4f0faf7df114a',
                            'size': '2539928197'},
        'pubDate': 'Fri, 26 Aug 2016 21:53:10 -0400',
        'title': 'War Dogs 2016 HD-TS x264-CPG'},

    {   'category': 'Movie > HD',
        'comments': 'https://6box.me/details/b2912874f57f5db608b461ac7ef93c0b#comments',
        'description': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv',
        'guid': 'https://6box.me/details/b2912874f57f5db608b461ac7ef93c0b',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/b2912874f57f5db608b461ac7ef93c0b.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2040',
                            'guid': 'b2912874f57f5db608b461ac7ef93c0b',
                            'size': '870948971'},
        'pubDate': 'Fri, 26 Aug 2016 17:29:55 -0400',
        'title': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv'},

    {   'category': 'Movie > HD',
        'comments': 'https://6box.me/details/371f08b393fec217f1cc55c49d555807#comments',
        'description': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv',
        'guid': 'https://6box.me/details/371f08b393fec217f1cc55c49d555807',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/371f08b393fec217f1cc55c49d555807.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2040',
                            'guid': '371f08b393fec217f1cc55c49d555807',
                            'size': '870948761'},
        'pubDate': 'Fri, 26 Aug 2016 17:29:56 -0400',
        'title': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv'},

    {   'category': 'Movie > HD',
        'comments': 'https://6box.me/details/f24e0842072a6776851adab687643229#comments',
        'description': 'war dogs 2016 readnfo cam x264 ac3 titan mkv',
        'guid': 'https://6box.me/details/f24e0842072a6776851adab687643229',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/f24e0842072a6776851adab687643229.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2040',
                            'guid': 'f24e0842072a6776851adab687643229',
                            'size': '837175678'},
        'pubDate': 'Fri, 26 Aug 2016 12:02:35 -0400',
        'title': 'war dogs 2016 readnfo cam x264 ac3 titan mkv'},

    {   'category': 'Movie > HD',
        'comments': 'https://6box.me/details/e0c481ced7eb876a25440aac6a36bcf9#comments',
        'description': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv',
        'guid': 'https://6box.me/details/e0c481ced7eb876a25440aac6a36bcf9',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/e0c481ced7eb876a25440aac6a36bcf9.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2040',
                            'guid': 'e0c481ced7eb876a25440aac6a36bcf9',
                            'size': '834554318'},
        'pubDate': 'Fri, 26 Aug 2016 12:09:45 -0400',
        'title': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv'},

    {   'category': 'Movies > HD',
        'comments': 'https://www.tabula-rasa.pw/details/d5bd46d3604f843e88c5138b657e23affb28e6d8#comments',
        'description': 'War Dogs 2016 HD-TS x264-CPG - "War.Dogs.2016.HD-TS.x264-CPG.par2" - (02/53) ',
        'guid': 'https://www.tabula-rasa.pw/details/d5bd46d3604f843e88c5138b657e23affb28e6d8',
        'indexer': 'Tabula-Rasa',
        'link': 'https://www.tabula-rasa.pw/getnzb/d5bd46d3604f843e88c5138b657e23affb28e6d8.nzb&i=1178&r=d14119a6316fc450bb837e9d84b01e4c',
        'newznab_attr': {   'category': '2040',
                            'comments': '0',
                            'coverurl': 'https://www.tabula-rasa.pw/covers/movies/2005151-cover.jpg',
                            'files': '52',
                            'grabs': '2',
                            'group': 'alt.binaries.mom',
                            'imdb': '2005151',
                            'password': '0',
                            'poster': 'misterx66@gmail.com (misterX66)',
                            'size': '2459067437',
                            'usenetdate': 'Sat, 27 Aug 2016 12:38:07 +0200'},
        'pubDate': 'Sat, 27 Aug 2016 16:32:43 +0200',
        'title': 'War Dogs 2016 HD-TS x264-CPG - "War.Dogs.2016.HD-TS.x264-CPG.par2" - (02/53) '},

    {   'category': 'Movie > SD',
        'comments': 'https://6box.me/details/a0a215e5cea058e177e2b4c257d9c3f6#comments',
        'description': 'war dogs 2016 hd-ts x264-cpg',
        'guid': 'https://6box.me/details/a0a215e5cea058e177e2b4c257d9c3f6',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/a0a215e5cea058e177e2b4c257d9c3f6.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2030',
                            'guid': 'a0a215e5cea058e177e2b4c257d9c3f6',
                            'size': '2589310900'},
        'pubDate': 'Fri, 26 Aug 2016 23:24:44 -0400',
        'title': 'war dogs 2016 hd-ts x264-cpg'},

    {   'category': 'Movie > HD',
        'comments': 'https://6box.me/details/eeb541d8c64f544ce9a32f4a24efdbce#comments',
        'description': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv',
        'guid': 'https://6box.me/details/eeb541d8c64f544ce9a32f4a24efdbce',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/eeb541d8c64f544ce9a32f4a24efdbce.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2040',
                            'guid': 'eeb541d8c64f544ce9a32f4a24efdbce',
                            'size': '870957781'},
        'pubDate': 'Fri, 26 Aug 2016 21:41:44 -0400',
        'title': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv'},

    {   'category': 'Movie > HD',
        'comments': 'https://6box.me/details/3e6a50bdf2f0e897dd39aa7aa9196d77#comments',
        'description': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv',
        'guid': 'https://6box.me/details/3e6a50bdf2f0e897dd39aa7aa9196d77',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/3e6a50bdf2f0e897dd39aa7aa9196d77.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2040',
                            'guid': '3e6a50bdf2f0e897dd39aa7aa9196d77',
                            'size': '870956706'},
        'pubDate': 'Fri, 26 Aug 2016 21:41:43 -0400',
        'title': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv'},

    {   'category': 'Movie > SD',
        'comments': 'https://6box.me/details/0e820dde0ad4260256b4f0faf7df114a#comments',
        'description': 'War Dogs 2016 HD-TS x264-CPG',
        'guid': 'https://6box.me/details/0e820dde0ad4260256b4f0faf7df114a',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/0e820dde0ad4260256b4f0faf7df114a.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2030',
                            'guid': '0e820dde0ad4260256b4f0faf7df114a',
                            'size': '2539928197'},
        'pubDate': 'Fri, 26 Aug 2016 21:53:10 -0400',
        'title': 'War Dogs 2016 HD-TS x264-CPG'},

    {   'category': 'Movie > HD',
        'comments': 'https://6box.me/details/b2912874f57f5db608b461ac7ef93c0b#comments',
        'description': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv',
        'guid': 'https://6box.me/details/b2912874f57f5db608b461ac7ef93c0b',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/b2912874f57f5db608b461ac7ef93c0b.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2040',
                            'guid': 'b2912874f57f5db608b461ac7ef93c0b',
                            'size': '870948971'},
        'pubDate': 'Fri, 26 Aug 2016 17:29:55 -0400',
        'title': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv'},

    {   'category': 'Movie > HD',
        'comments': 'https://6box.me/details/371f08b393fec217f1cc55c49d555807#comments',
        'description': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv',
        'guid': 'https://6box.me/details/371f08b393fec217f1cc55c49d555807',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/371f08b393fec217f1cc55c49d555807.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2040',
                            'guid': '371f08b393fec217f1cc55c49d555807',
                            'size': '870948761'},
        'pubDate': 'Fri, 26 Aug 2016 17:29:56 -0400',
        'title': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv'},

    {   'category': 'Movie > HD',
        'comments': 'https://6box.me/details/f24e0842072a6776851adab687643229#comments',
        'description': 'war dogs 2016 readnfo cam x264 ac3 titan mkv',
        'guid': 'https://6box.me/details/f24e0842072a6776851adab687643229',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/f24e0842072a6776851adab687643229.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2040',
                            'guid': 'f24e0842072a6776851adab687643229',
                            'size': '837175678'},
        'pubDate': 'Fri, 26 Aug 2016 12:02:35 -0400',
        'title': 'war dogs 2016 readnfo cam x264 ac3 titan mkv'},

    {   'category': 'Movie > HD',
        'comments': 'https://6box.me/details/e0c481ced7eb876a25440aac6a36bcf9#comments',
        'description': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv',
        'guid': 'https://6box.me/details/e0c481ced7eb876a25440aac6a36bcf9',
        'indexer': '6box',
        'link': 'https://6box.me/getnzb/e0c481ced7eb876a25440aac6a36bcf9.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
        'newznab_attr': {   'category': '2040',
                            'guid': 'e0c481ced7eb876a25440aac6a36bcf9',
                            'size': '834554318'},
        'pubDate': 'Fri, 26 Aug 2016 12:09:45 -0400',
        'title': 'War Dogs 2016 READNFO CAM X264 AC3 TiTAN mkv'},

    {   'category': 'Movies > HD',
        'comments': 'https://www.tabula-rasa.pw/details/d5bd46d3604f843e88c5138b657e23affb28e6d8#comments',
        'description': 'War Dogs 2016 HD-TS x264-CPG - "War.Dogs.2016.HD-TS.x264-CPG.par2" - (02/53) ',
        'guid': 'https://www.tabula-rasa.pw/details/d5bd46d3604f843e88c5138b657e23affb28e6d8',
        'indexer': 'Tabula-Rasa',
        'link': 'https://www.tabula-rasa.pw/getnzb/d5bd46d3604f843e88c5138b657e23affb28e6d8.nzb&i=1178&r=d14119a6316fc450bb837e9d84b01e4c',
        'newznab_attr': {   'category': '2040',
                            'comments': '0',
                            'coverurl': 'https://www.tabula-rasa.pw/covers/movies/2005151-cover.jpg',
                            'files': '52',
                            'grabs': '2',
                            'group': 'alt.binaries.mom',
                            'imdb': '2005151',
                            'password': '0',
                            'poster': 'misterx66@gmail.com (misterX66)',
                            'size': '2459067437',
                            'usenetdate': 'Sat, 27 Aug 2016 12:38:07 +0200'},
        'pubDate': 'Sat, 27 Aug 2016 16:32:43 +0200',
        'title': 'War Dogs 2016 HD-TS x264-CPG - "War.Dogs.2016.HD-TS.x264-CPG.par2" - (02/53) '}]
"""
