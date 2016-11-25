import dominate
from dominate.tags import *
import json
import core
from core import sqldb
from core.conversions import Conversions


class MovieStatusPopup():

    def __init__(self):
        self.sql = sqldb.SQL()

    def html(self, imdbid):

        data = self.sql.get_movie_details(imdbid)
        if data:
            poster_path = 'images/posters/{}.jpg'.format(data['imdbid'])
            title_date = data['title'] + " " + str( data['year'] )

            tomatoes_url = data['tomatourl']

        doc = dominate.document(title='Watcher')

        with doc.head:
            base(href="/static/")
            script(src='js/status/movie_status_popup.js')

        with doc:
            with div(id='container'):
                if not data:
                    span('Unable to get movie information from database. Check logs for more information.')
                    return doc.render()

                with div(id='title'):
                    with p():
                        span(title_date, id='title', imdbid=imdbid)
                        button('CLOSE', id='close')
                        button('SEARCH NOW', id='search_now', imdbid=data['imdbid'], title=data['title'])
                with div(id='media'):
                    img(id='poster', src=poster_path)
                    with div(id='search_results'):

                        with ul(id='result_list'):
                             self.result_list(imdbid)
                        div(id='results_thinker')

                with div(id='plot'):
                    p(data['plot'])
                with div(id='additional_info'):
                    with a(href=tomatoes_url, target='_blank'):
                        span('Rotten Tomatoes Rating: {}'.format(data['tomatorating']) )
                    span('Theatrical Release Date: {}'.format(data['released']))
                    span('DVD Release Date: {}'.format(data['dvd']))
                    button('REMOVE', id='remove')

        return doc.render()

    def result_list(self, imdbid):
        results = self.sql.get_search_results(imdbid)
        doc = dominate.document(title='Watcher')
        with doc:

            if not results:
                li('Nothing found yet.', cls='title bold')
                li('Next automatic search scheduled for: {}'.format(Conversions.human_datetime(core.NEXT_SEARCH)), cls='title')
            else:
                for idx, res in enumerate(results):
                    info_link = res['info_link']
                    title = res['title']
                    guid = res['guid']
                    status = res['status']
                    size = Conversions.human_file_size( res['size'] )
                    pubdate = res['pubdate']

                    # applied bottom border to all but last element
                    if idx == len(results) - 1:
                        bbord = ''
                    else:
                        bbord = 'bbord'
                    with li(cls='title bold'):
                        span(res['title'], cls='name')
                        with span(cls='buttons'):
                            with a(href=info_link, target='_blank'):
                                i('info_outline', cls='material-icons')

                            i('file_download', cls='material-icons manual_download', imdbid=imdbid, guid=guid)

                            i('delete_forever', cls='material-icons mark_bad', guid=guid)

                    with li(cls='data '+ bbord):
                        span(' Status: ')
                        if status == 'Snatched':
                            span(status, cls='bold snatched')
                        elif status == 'Bad':
                            span(status, cls='bold bad')
                        elif status == 'Finished':
                            span(status, cls='bold finished')
                        else:
                            span(status, cls='bold')
                        span(' Size: ')
                        span(size, cls='bold')
                        span( ' Score: ')
                        span(res['score'], cls='bold')
                        span(' Source: ')
                        span(res['indexer'], cls='bold')
                        span(' Published: ')
                        span(pubdate, cls='bold')

        return doc.render()
