from dominate.tags import *


class Header():
    @staticmethod
    def insert_header(current):

        with div(id='header'):
            with div(id='header_container'):
                img(src='images/logo.png', alt='')
                with ul(id='nav'):
                    if current == 'settings':
                        cls = 'settings current'
                    else:
                        cls = 'settings'
                    with li('Settings', cls=cls):
                            with ul(cls='settings_menu'):
                                with a(href='/settings/server'):
                                    with li():
                                        i(cls='fa fa-server')
                                        span('Server')
                                with a(href='/settings/search'):
                                    with li():
                                        i(cls='fa fa-search')
                                        span('Search')
                                with a(href='/settings/quality'):
                                    with li():
                                        i(cls='fa fa-filter')
                                        span('Quality')
                                with a(href='/settings/providers'):
                                    with li():
                                        i(cls='fa fa-plug')
                                        span('Providers')
                                with a(href='/settings/downloader'):
                                    with li():
                                        i(cls='fa fa-download')
                                        span('Downloader')
                                with a(href='/settings/postprocessing'):
                                    with li():
                                        i(cls='fa fa-film')
                                        span('Post Processing')


                    with a(href='/add_movie'):
                        if current == 'add_movie':
                            cls = 'add_movie current'
                        else:
                            cls = 'add_movie'
                        li('Add Movie', cls=cls)

                    with a(href='/status'):
                        if current == 'status':
                            cls = 'status current'
                        else:
                            cls = 'status'
                        li('Status', cls=cls)
