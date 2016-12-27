import datetime

import core
import dominate
from cherrypy import expose
from core import sqldb, version
from dominate.tags import *
from header import Header
from head import Head


class Status():

    def __init__(self):
        return

    @expose
    def index(self):
        doc = dominate.document(title='Watcher')

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href='static/css/status.css')
            link(rel='stylesheet', href='static/css/movie_status_popup.css')
            script(type='text/javascript', src='static/js/status/main.js')

        with doc:
            Header.insert_header(current="status")
            with div(id='content'):

                    with ul(id='movie_list'):
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

        doc = dominate.document(title='Watcher')
        with doc:
            for data in movies:
                title_year = u'{} {}'.format(data['title'], data['year'])
                poster_path = 'static/images/posters/{}.jpg'.format(data['imdbid'])
                with li(cls='movie', imdbid=data['imdbid']):
                    with div():
                        status = data['status']
                        if status == 'Wanted':
                            span('Wanted', cls='status wanted')
                        elif status == 'Found':
                            span('Found', cls='status found')
                        elif status == 'Snatched':
                            span('Snatched', cls='status snatched')
                        elif status == 'Downloading':
                            span('Downloading', cls='status downloading')
                        elif status == 'Finished':
                            span('Finished', cls='status finished')
                        else:
                            span('Status Unknown', cls='status wanted')

                        img(src=poster_path, alt='Poster for {}'.format(data['imdbid']))

                        span(title_year, cls='title_year')

        return doc.render()
