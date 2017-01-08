import json
import logging
from datetime import datetime

import core
from core import sqldb
from fuzzywuzzy import fuzz

logging = logging.getLogger(__name__)


class ScoreResults():

    def __init__(self):
        self.sql = sqldb.SQL()
        return

    # returns list of dictionary results after filtering and scoring
    def score(self, results, imdbid, type):
        ''' Scores and filters search results.
        :param results: list of dicts of search results
        :param imdbid: str imdb identification number (tt123456)
        :param type: str 'nzb' or 'torrent'

        Iterates over the list and filters movies based on Words.
        Scores movie based on reslution priority, title match, and
            preferred words,

        Orders the list by Score, then by Size. So a 5gb release will have
            a lower index than a 2gb release of the same score.

        Returns list of dicts.
        '''

        self.results = results

        tableresults = self.sql.get_movie_details('imdbid', imdbid)

        title = tableresults['title']

        if tableresults['quality']:
            quality_dict = json.loads(tableresults['quality'])
            qualities = quality_dict['Quality']
            filters = quality_dict['Filters']
        else:
            qualities = core.CONFIG['Quality']
            filters = core.CONFIG['Filters']

        retention = int(core.CONFIG['Search']['retention'])
        score_title = core.CONFIG['Search']['score_title'].lower() == 'true'
        required = filters['requiredwords'].lower().split(',')
        preferred = filters['preferredwords'].lower().split(',')
        ignored = filters['ignoredwords'].lower().split(',')
        today = datetime.today()

        # These all just modify self.results
        self.reset()
        self.remove_inactive()
        self.remove_ignored(ignored)
        self.keep_required(required)
        self.retention_check(retention, today)
        self.score_quality(qualities)
        if score_title:
            self.fuzzy_title(title)
        self.score_preferred(preferred)

        return self.results

    def reset(self):
        for i, d in enumerate(self.results):
            self.results[i]['score'] = 0

    def remove_inactive(self):
        ''' Removes results from indexers no longer enabled

        Pulls active indexers from config, then removes any
            result that isn't from an active indexer.

        Does not return, modifies self.results
        '''

        active = []
        for i in core.CONFIG['Indexers'].values():
            if i[2] == 'true':
                active.append(i[0])

        keep = []
        for indexer in active:
            for result in self.results:
                if indexer in result['guid']:
                    keep.append(result)

        self.results = keep
        return

    def remove_ignored(self, words):
        ''' Remove results with ignored 'words'
        :param words: list of forbidden words

        Iterates through self.results and removes any entry that contains
            any 'words'

        Does not return
        '''

        if not words:
            return
        for word in words:
            if word == '':
                continue
            else:
                self.results = [r for r in self.results if word not in r['title'].lower()]

    def keep_required(self, words):
        ''' Remove results without required 'words'
        :param words: list of required words

        Iterates through self.results and removes any entry that does not
            contain all 'words'

        Does not return
        '''

        if not words:
            return
        for word in words:
            if word == '':
                continue
            else:
                self.results = [r for r in self.results if word in r['title'].lower()]

    def retention_check(self, retention, today):
        ''' Remove results older than 'retention' days
        :param retention: int days of retention limit
        :param today: datetime obj today's date

        Iterates through self.results and removes any entry that was published
            more than 'retention' days ago

        Does not return
        '''

        if retention == 0:
            return
        lst = []
        for result in self.results:
            if result['type'] != 'nzb':
                lst.append(result)
            else:
                pubdate = datetime.strptime(result['pubdate'], '%d %b %Y')
                age = (today - pubdate).days
                if age < retention:
                    lst.append(result)
        self.results = lst

    def score_preferred(self, words):
        ''' Increase score for each 'words' match
        :param words: list of preferred words

        Iterates through self.results and increases ['score'] each time a
            preferred 'words' is found

        Does not return
        '''

        if not words:
            return
        for word in words:
            if word == '':
                continue
            else:
                for result in self.results:
                    if word in result['title'].lower():
                        result['score'] += 10

    def fuzzy_title(self, title):
        ''' Score and remove results based on title match
        :param title: str title of movie

        Iterates through self.results and removes any entry that does not
            fuzzy match 'title' > 60.
        Adds fuzzy_score / 20 points to ['score']

        Does not return
        '''

        lst = []
        for result in self.results:
            title = title.replace(' ', '.').replace(':', '.').lower()
            test = result['title'].replace(' ', '.').lower()
            match = fuzz.partial_ratio(title, test)
            if match > 60:
                result['score'] += (match / 20)
                lst.append(result)
        self.results = lst

    def score_quality(self, qualities):
        ''' Score releases based on quality preferences
        :param qualities: dict of quality preferences from MOVIES table

        Iterates through self.results and removes any entry that does not
            fit into quality criteria (resoution, filesize)
        Adds to ['score'] based on resolution priority

        Does not return
        '''

        lst = []
        for result in self.results:
            resolution = result['resolution']
            size = result['size'] / 1000000
            for quality in qualities:
                qlist = qualities[quality]
                if qlist[0] != 'true':
                    continue
                priority = int(qlist[1])
                min_size = int(qlist[2])
                max_size = int(qlist[3])

                if resolution == quality:
                    if min_size < size < max_size:
                        result['score'] += (8 - priority) * 100
                        lst.append(result)
        self.results = lst


"""
SCORING COLUMNS. I swear some day this will make sense.

4321

<4>
0-4
Resolution Match. Starts at 8.
Remove 1 point for the priority of the matched resolution.
So if we want 1080P then 720P in that order, 1080 movies will get 0 points
    removed, where 720P will get 1 point removed.
We do this because the jquery sortable gives higher priority items a lower
    number, so 0 is the most important item. This allows a large amount of
    preferred word matches to overtake a resolution match.

<3-1>
0-100
Add 10 points for every preferred word match.

"""
