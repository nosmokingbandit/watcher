import datetime

import core
import dominate
from cherrypy import expose
from core import sqldb, version
from dominate.tags import *
from header import Header


class Status():

    def __init__(self):
        self.version = version.Version()
        return

    @expose
    def index(self):
        self.update_check()

        doc = dominate.document(title='Watcher')

        with doc.head:
            base(href="/static/")

            link(rel='stylesheet', href='css/style.css')
            link(rel='stylesheet', href='css/status.css')
            link(rel='stylesheet', href='css/movie_status_popup.css')
            link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')
            link(rel='stylesheet', href='font-awesome/css/font-awesome.css')
            link(rel='stylesheet', href='js/sweetalert-master/dist/sweetalert.css')

            script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js')
            script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.0/jquery-ui.min.js')
            script(type='text/javascript', src='js/sweetalert-master/dist/sweetalert-dev.js')
            script(type='text/javascript', src='js/status/main.js')

        with doc:
            Header.insert_header(current="status")
            with div(id='content'):

                    with ul(id='movie_list'):
                        self.movie_list()

            if core.UPDATE_STATUS is not None:
                if core.UPDATE_STATUS['status'] == 'behind':
                    commit = 'commit'
                    if core.UPDATE_STATUS['behind_count'] > 1:
                        commit = 'commits'
                    message = 'Update available. You are {} {} behind.'.format(core.UPDATE_STATUS['behind_count'], commit)
                    href = '{}/compare/{}...{}'.format(core.GIT_URL, core.UPDATE_STATUS['local_hash'], core.UPDATE_STATUS['new_hash'])

                    with div(id='update_footer'):
                        with div(id='footer_container'):
                            with span(cls='updatemsg'):
                                a(message, href=href, target='_blank')
                                button('Update Now', id='update_now')

                elif core.UPDATE_STATUS['status'] == 'error':
                    message = 'Error checking for updates.'
                    err = core.UPDATE_STATUS['error']

                    with div(id='update_footer'):
                        with div(id='footer_container'):
                            span(message, cls='errormsg')
                            span(err, cls='errormsg')

            div(id='overlay')
            div(id='status_pop_up')

        return doc.render()

    @staticmethod
    def movie_list():
        movies = sqldb.SQL().get_user_movies()
        if not movies:
            html = 'Error retrieving list of user\'s movies. Check logs for more information'
            return html

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

                        img(src=poster_path, alt='Poster for {}'.format(data['imdbid']))

                        span(title_year, cls='title_year')

        return doc.render()

    def update_check(self):
        if core.CONFIG['Server']['checkupdates'] == 'false':
            return None

        now = datetime.datetime.now()
        if core.UPDATE_LAST_CHECKED is not None:
            hours_since_last = (now - core.UPDATE_LAST_CHECKED).seconds / 3600
            if hours_since_last >= int(core.CONFIG['Server']['checkupdatefrequency']):
                core.UPDATE_LAST_CHECKED = now
                return self.version.manager.update_check()
            else:
                return None
        else:
            # This will happen on first open of /status
            core.UPDATE_LAST_CHECKED = now
            return self.version.manager.update_check()
