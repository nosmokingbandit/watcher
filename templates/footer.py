from dominate.tags import *
import core


class Footer():
    @staticmethod
    def insert_footer():

        with div(cls='footer clearfix'):
            i(cls='fa fa-copyright')
            with span('2016-2017 Watcher '):
                with a(href='https://www.gnu.org/licenses/gpl-3.0.en.html',title='GNU GPL v3',target='_blank'):
                    span('(GNU GPL v3)')
                div()
                with a(href='https://github.com/nosmokingbandit/watcher',title='Link to the Watcher Git repository',target='_blank'):
                    span('Contribute and report issues to the Watcher Git.')
