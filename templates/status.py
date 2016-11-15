from cherrypy import expose
import dominate
from dominate.tags import *
from core import sqldb
from header import Header

class Status():

    def __init__(self):
        return

    @expose
    def index(self):
        doc = dominate.document(title='Watcher')

        with doc.head:
            base(href="/static/")

            link(rel='stylesheet', href='css/style.css')
            link(rel='stylesheet', href='css/status.css')
            link(rel='stylesheet', href='css/movie_status_popup.css')
            link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')

            script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js')

            script(type='text/javascript', src='js/status/main.js')


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


        doc = dominate.document(title='Watcher')
        with doc:
            for data in movies:
                title_year = '{} {}'.format(data['title'], data['year'])
                poster_path = 'images/posters/{}.jpg'.format(data['imdbid'])
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
                            print '**INFO: Status of {} is {}, we don\'t know what that means.'.format(data['imdbid'], data['status'])

                        img(src=poster_path, alt='Poster for {}'.format(data['imdbid']))

                        span(title_year, cls='title_year')

        return doc.render()
