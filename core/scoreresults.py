import logging
from datetime import datetime

import json
import core
from core import sqldb
from fuzzywuzzy import fuzz

logging = logging.getLogger(__name__)


class ScoreResults():

    def __init__(self):
        self.sql = sqldb.SQL()
        return

    # returns list of dictionary results after filtering and scoring
    def score(self, results, imdbid=None, quality_profile=None):
        ''' Scores and filters search results.
        results: list of dicts of search results
        imdbid: str imdb identification number (tt123456)   <optional*>
        quality_profile: str quality profile name           <optional*>

        Either imdbid or quality_profile MUST be passed.

        If imdbid passed, finds quality in database row.
        If profile_quality passed, uses that quality and ignores db.

        quality_profile can be set to 'import', which uses 'Default' settings,
            but doesn't allow the result to be filtered out.

        Iterates over the list and filters movies based on Words.
        Scores movie based on reslution priority, title match, and
            preferred words,

        Word groups are split in to a list of lists:
        [['word'], ['word2', 'word3'], 'word4']

        Returns list of dicts.
        '''

        if imdbid is None and quality_profile is None:
            logging.warning('Neither imdbid or quality_profile passed.')
            return results

        self.results = results

        if quality_profile is None:
            movie_details = self.sql.get_movie_details('imdbid', imdbid)
            quality_profile = movie_details['quality']
            title = movie_details['title']
        else:
            title = None

        if quality_profile == 'import':
            quality = self.import_quality()
        elif quality_profile in core.CONFIG['Quality']['Profiles']:
            quality = core.CONFIG['Quality']['Profiles'][quality_profile]
        else:
            quality = core.CONFIG['Quality']['Profiles']['Default']

        resolution = {k: v for k, v in quality.iteritems() if k in ['4K', '1080P', '720P', 'SD']}
        retention = core.CONFIG['Search']['retention']
        seeds = core.CONFIG['Search']['mintorrentseeds']

        required = [i.split('&') for i in quality['requiredwords'].lower().replace(' ', '').split(',') if i != '']
        preferred = [i.split('&') for i in quality['preferredwords'].lower().replace(' ', '').split(',') if i != '']
        ignored = [i.split('&') for i in quality['ignoredwords'].lower().replace(' ', '').split(',') if i != '']

        today = datetime.today()

        # These all just modify self.results
        self.reset()
        self.remove_inactive()
        self.remove_ignored(ignored)
        self.keep_required(required)
        self.retention_check(retention, today)
        self.seed_check(seeds)
        self.score_resolution(resolution)
        if quality['scoretitle']:
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

        Does not filter Torrent results.
            Since torrent names don't always match their domain
            ie demonoid == dnoid.me, we can't filter out disabled torrent
            indexers since all would be removed

        Does not return, modifies self.results
        '''

        active = []
        for i in core.CONFIG['Indexers']['NewzNab'].values():
            if i[2] is True:
                active.append(i[0])

        keep = []
        for result in self.results:
            if result['type'] in ['torrent', 'magnet', 'import']:
                keep.append(result)
            for indexer in active:
                if indexer in result['guid']:
                    keep.append(result)

        self.results = keep
        return

    def remove_ignored(self, group_list):
        ''' Remove results with ignored groups of 'words'
        :param group_list: list of forbidden groups of words

        word_groups is a list of lists.

        Iterates through self.results and removes every entry that contains
            any group of 'words'
        A group of 'words' is multiple 'words' concatenated with an ampersand '&'

        Does not return
        '''

        keep = []

        if not group_list or group_list == [u'']:
            return

        for r in self.results:
            cond = False
            for word_group in group_list:
                if all(word in r['title'].lower() for word in word_group):
                    cond = True
                    break
            if cond is False and r not in keep:
                keep.append(r)
        self.results = keep

    def keep_required(self, group_list):
        ''' Remove results without required groups of 'words'
        :param word_goups: list of required groups of words

        Iterates through self.results and removes every entry that does not
            contain any group of 'words'
        A group of 'words' is multiple 'words' concatenated with an ampersand '&'

        Does not return
        '''

        keep = []

        if not group_list or group_list == [u'']:
            return

        for r in self.results:
            for word_group in group_list:
                if all(word in r['title'].lower() for word in word_group) and r not in keep:
                    keep.append(r)
                    break
                else:
                    continue
        self.results = keep

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
            if result['type'] != u'nzb':
                lst.append(result)
            else:
                pubdate = datetime.strptime(result['pubdate'], '%d %b %Y')
                age = (today - pubdate).days
                if age < retention:
                    lst.append(result)
        self.results = lst

    def seed_check(self, seeds):
        ''' Remove any torrents with fewer than 'seeds' seeders
        seeds: int # of seeds required

        Does not return
        '''

        if seeds == 0:
            return
        lst = []
        for result in self.results:
            if result['type'] not in ['torrent', 'magnet']:
                lst.append(result)
            else:
                if int(result['seeders']) >= seeds:
                    lst.append(result)
        self.results = lst

    def score_preferred(self, group_list):
        ''' Increase score for each group of 'words' match
        :param word_goups: list of preferred groups of words

        Iterates through self.results and increases ['score'] each time a
            preferred group of 'words' is found
        A group of 'words' is multiple 'words' concatenated with an ampersand '&'

        Does not return
        '''

        if not group_list or group_list == [u'']:
            return

        for r in self.results:
            for word_group in group_list:
                if all(word in r['title'].lower() for word in word_group):
                    r['score'] += 10
                    break
                else:
                    continue

    def fuzzy_title(self, title):
        ''' Score and remove results based on title match
        title: str title of movie   <optional*>

        Iterates through self.results and removes any entry that does not
            fuzzy match 'title' > 60.
        Adds fuzzy_score / 20 points to ['score']

        *If title is passed as None, assumes perfect match and scores +20

        Does not return
        '''

        lst = []
        if title is None:
            for result in self.results:
                result['score'] += 20
                lst.append(result)
        else:
            for result in self.results:
                title = title.replace(u' ', u'.').replace(u':', u'.').lower()
                test = result['title'].replace(u' ', u'.').lower()
                match = fuzz.token_set_ratio(title, test)
                if match > 60:
                    result['score'] += (match / 5)
                    lst.append(result)
        self.results = lst

    def score_resolution(self, resolutions):
        ''' Score releases based on quality preferences
        :param qualities: dict of quality preferences from MOVIES table

        Iterates through self.results and removes any entry that does not
            fit into quality criteria (resoution, filesize)
        Adds to ['score'] based on resolution priority

        Does not return
        '''

        lst = []
        for result in self.results:
            result_res = result['resolution']
            size = result['size'] / 1000000
            for k, v in resolutions.iteritems():
                if v[0] is False:
                    continue
                priority = v[1]
                min_size = v[2]
                max_size = v[3]
                if result_res == k:
                    if min_size < size < max_size:
                        result['score'] += (8 - priority) * 100
                        lst.append(result)
        self.results = lst

    def import_quality(self):
        profile = json.loads(json.dumps(core.CONFIG['Quality']['Profiles']['Default']))

        profile['ignoredwords'] = u''
        profile['requiredwords'] = u''
        resolutions = ['4K', '1080P', '720P', 'SD']

        for i in resolutions:
            if profile[i][0] is False:
                profile[i][1] = 4
                profile[i][0] = True

            profile[i][2] = 0
            profile[i][3] = Ellipsis

        return profile


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
