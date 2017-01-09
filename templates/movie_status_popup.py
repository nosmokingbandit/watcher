import json

import core
import dominate
from core import sqldb
from core.conversions import Conversions
from dominate.tags import *


class MovieStatusPopup():

    def __init__(self):
        self.sql = sqldb.SQL()

    def html(self, imdbid):

        data = self.sql.get_movie_details('imdbid', imdbid)
        if data:
            poster_path = core.URL_BASE + '/static/images/posters/{}.jpg'.format(data['imdbid'])
            title = data['title']
            year = str(data['year'])

            tomatoes_url = data['tomatourl']

        quality_settings = json.loads(data['quality'])

        container = div(id='container')
        with container:
            script(src=core.URL_BASE + '/static/js/status/movie_status_popup.js?v=01.03')
            if not data:
                span(u'Unable to get movie information from database. Check logs for more information.')
                return doc.render()

            with div(id='title'):
                with p():
                    with span(title, id='title', imdbid=imdbid):
                        span(year, id='title_year')
                    i(cls='fa fa-times', id='close')
                    i(cls='fa fa-trash', id='remove')
                    i(cls='fa fa-cog', id='change_quality')
                    i(cls='fa fa-save', id='save_quality')
                    i(cls='fa fa-search', id='search_now', imdbid=data['imdbid'], title=data['title'])
            with div(id='media'):
                img(id='poster', src=poster_path)
                with div(id='search_results'):

                    with ul(id='result_list'):
                        self.result_list(imdbid)
                    div(id='results_thinker')

                    # Panel that swaps in with quality adjustments
                    resolutions = ['4K', '1080P', '720P', 'SD']
                    with ul(id='quality', cls='wide'):
                        # Resolution Block
                        with ul(id='resolution', cls='sortable'):
                            span(u'Resolutions', cls='sub_cat not_sortable')

                            for res in resolutions:
                                prior = u'{}priority'.format(res)
                                with li(cls='rbord', id=prior, sort=quality_settings['Quality'][res][1]):
                                    i(cls='fa fa-bars')
                                    i(id=res, cls='fa fa-square-o checkbox', value=quality_settings['Quality'][res][0])
                                    span(res)

                        # Size restriction block
                        with ul(id='resolution_size'):
                            with li(u'Size Restrictions (MB)', cls='sub_cat'):

                                for res in resolutions:
                                    min = '{}min'.format(res)
                                    max = '{}max'.format(res)
                                    with li():
                                        span(res)
                                        input(type='number', id=min, value=quality_settings['Quality'][res][2], min='0', style='width: 7.5em')
                                        input(type='number', id=max, value=quality_settings['Quality'][res][3], min='0', style='width: 7.5em')

                        with ul(id='filters', cls='wide'):
                            with li(cls='bbord flexbox'):
                                span(u'Required words:')
                                input(type='text', id='requiredwords', value=quality_settings['Filters']['requiredwords'], style='width: 16em')
                            with li(cls='bbord flexbox'):
                                span(u'Preferred words:')
                                input(type='text', id='preferredwords', value=quality_settings['Filters']['preferredwords'], style='width: 16em')
                            with li(cls='flexbox'):
                                span(u'Ignored words:')
                                input(type='text', id='ignoredwords', value=quality_settings['Filters']['ignoredwords'], style='width: 16em')

            with div(id='plot'):
                p(data['plot'])
            with div(id='additional_info'):
                with a(href=tomatoes_url, target='_blank'):
                    span(u'Rotten Tomatoes Rating: {}'.format(data['tomatorating']))
                span(u'Theatrical Release Date: {}'.format(data['released']))
                span(u'DVD Release Date: {}'.format(data['dvd']))

        return unicode(container)

    def result_list(self, imdbid):
        results = self.sql.get_search_results(imdbid)
        doc = dominate.document(title='Watcher')  # FIX
        with doc:

            if not results:
                li(u'Nothing found yet.', cls='title bold')
                li(u'Next automatic search scheduled for: {}'.format(Conversions.human_datetime(core.NEXT_SEARCH)), cls='title')
            else:
                for idx, res in enumerate(results):
                    info_link = res['info_link']
                    title = res['title']
                    guid = res['guid']
                    status = res['status']
                    size = Conversions.human_file_size(res['size'])
                    pubdate = res['pubdate']

                    # applied bottom border to all but last element
                    if idx == len(results) - 1:
                        bbord = u''
                    else:
                        bbord = u'bbord'
                    with li(cls='title bold'):
                        span(title, cls='name', title=title)
                        with span(cls='buttons'):
                            with a(href=info_link, target='_blank'):
                                i(cls='fa fa-info-circle')
                            i(cls='fa fa-download', id='manual_download', imdbid=imdbid, guid=guid)
                            i(cls='fa fa-ban', id='mark_bad', guid=guid)
                    with li(cls='data ' + bbord):
                        span(u' Status: ')
                        if status == 'Snatched':
                            span(status, cls='bold snatched')
                        elif status == 'Bad':
                            span(status, cls='bold bad')
                        elif status == 'Finished':
                            span(status, cls='bold finished')
                        else:
                            span(status, cls='bold')
                        span(u' Size: ')
                        span(size, cls='bold')
                        span(u' Score: ')
                        span(res['score'], cls='bold')
                        span(u' Source: ')
                        span(res['indexer'] or '', cls='bold')
                        span(u' Published: ')
                        span(pubdate, cls='bold')

        return doc.render()

# pylama:ignore=W0401
