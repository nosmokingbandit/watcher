from dominate.tags import *
import core


class Header():
    @staticmethod
    def insert_header(current):
        
        Header.notification()

        with div(id='header'):
            with div(id='header_container'):
                img(src='static/images/logo.png', alt='')
                with ul(id='nav'):
                    if current == 'settings':
                        cls = 'settings current'
                    else:
                        cls = 'settings'
                    with li('Settings', cls=cls):
                            with ul(cls='settings_menu'):
                                with a(href='settings/server'):
                                    with li():
                                        i(cls='fa fa-server')
                                        span('Server')
                                with a(href='settings/search'):
                                    with li():
                                        i(cls='fa fa-search')
                                        span('Search')
                                with a(href='settings/quality'):
                                    with li():
                                        i(cls='fa fa-filter')
                                        span('Quality')
                                with a(href='settings/providers'):
                                    with li():
                                        i(cls='fa fa-plug')
                                        span('Providers')
                                with a(href='settings/downloader'):
                                    with li():
                                        i(cls='fa fa-download')
                                        span('Downloader')
                                with a(href='settings/postprocessing'):
                                    with li():
                                        i(cls='fa fa-film')
                                        span('Post Processing')

                    with a(href='add_movie'):
                        if current == 'add_movie':
                            cls = 'add_movie current'
                        else:
                            cls = 'add_movie'
                        li('Add Movie', cls=cls)

                    with a(href='status'):
                        if current == 'status':
                            cls = 'status current'
                        else:
                            cls = 'status'
                        li('Status', cls=cls)

    @staticmethod
    def notification():

        with ul(id='notif_list'):
            for index, notif in enumerate(core.NOTIFICATIONS):
                if notif is None:
                    continue

                with li(cls='notif', index=index):
                    with a(href=notif['title_link'], target='_none'):
                        with div(cls='notif_title'):
                            i(cls='fa ' + notif['icon'])
                            span(notif['title'])
                    div(notif['text'], cls='notif_text')
                    with div(cls='notif_footer'):
                        with span(cls='dismiss', index=index):
                            i(cls='fa fa-times')
                            span('Dismiss')
                        if notif['button']:
                            with a(href=notif['button'][1], cls='button', index=index):
                                ico = 'fa ' + notif['button'][2]
                                i(cls=ico)
                                span(notif['button'][0])
