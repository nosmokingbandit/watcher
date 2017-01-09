import core
import dominate
from cherrypy import expose
from core import sqldb
from dominate.tags import *
from header import Header
from head import Head


class Status():

    @expose
    def default(self):
        doc = dominate.document(title='Watcher')
        doc.attributes['lang'] = 'en'

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/status.css')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/status.css'.format(core.THEME))
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/movie_status_popup.css')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/movie_status_popup.css'.format(core.THEME))
            script(type='text/javascript', src=core.URL_BASE + '/static/js/status/main.js?v=12.27')

        with doc:
            Header.insert_header(current="status")
            with div(id='content'):
                self.movie_list()
            div(id='overlay')
            div(id='status_pop_up')

        return doc.render()

    @staticmethod
    def movie_list():
        movies = sqldb.SQL().get_user_movies()

        if movies == []:
            return None
        elif not movies:
            html = 'Error retrieving list of user\'s movies. Check logs for more information'
            return html

        movie_list = ul(id='movie_list')
        with movie_list:
            for data in movies:
                poster_path = core.URL_BASE + '/static/images/posters/{}.jpg'.format(data['imdbid'])
                with li(cls='movie', imdbid=data['imdbid']):
                    with div():
                        status = data['status']
                        if status == 'Wanted':
                            span(u'Wanted', cls='status wanted')
                        elif status == 'Found':
                            span(u'Found', cls='status found')
                        elif status == 'Snatched':
                            span(u'Snatched', cls='status snatched')
                        elif status == 'Downloading':
                            span(u'Downloading', cls='status downloading')
                        elif status == 'Finished':
                            span(u'Finished', cls='status finished')
                        else:
                            span(u'Status Unknown', cls='status wanted')

                        img(src=poster_path, alt='Poster for {}'.format(data['imdbid']))

                        with span(data['title'], cls='title_year'):
                            br()
                            span(data['year'])

        return unicode(movie_list)

# pylama:ignore=W0401
