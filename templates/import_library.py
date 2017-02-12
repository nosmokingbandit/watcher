import core
import dominate
from cherrypy import expose
from dominate.tags import *
from header import Header
from head import Head


class ImportLibrary():

    @expose
    def default(self):
        doc = dominate.document(title='Watcher')
        doc.attributes['lang'] = 'en'

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/import_library.css?v=02.09')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/import_library.css?v=02.09'.format(core.CONFIG['Server']['theme']))
            script(type='text/javascript', src=core.URL_BASE + '/static/js/import_library/main.js?v=02.09')

        with doc:
            Header.insert_header(current=None)
            with div(id='content'):
                h1('Import Library')
                with div(id='scan_dir'):
                    with div(id='directory_info'):
                        span('Library directory: ')
                        input(id='directory', type='text', placeholder=' /movies')
                        br()
                        span('Minimum file size to import: ')
                        input(id='minsize', type='number', value='500')
                        span('MB.')
                        br()
                        i(cls='fa fa-check-square checkbox', id='recursive', value='True')
                        span('Scan recursively.')
                        with div():
                            with span(id='start_scan'):
                                i(cls='fa fa-binoculars', id='start_scan')
                                span('Start scan')
                with div(id='wait'):
                    span('Scanning library for new movies.')
                    br()
                    span('This may take several minutes.')
                with div(id='list_files'):
                    with span('No movies found.', id='not_found'):
                        br()
                        with a(href='{}/import_library'.format(core.URL_BASE)):
                            i(cls='fa fa-caret-left')
                            span('Return')
                    with div(id='review'):
                        span('The following files have been found.', cls='title')
                        br()
                        span('Review and un-check any unwanted files.', cls='title')
                        table(id='files')
                    with div(id='incomplete'):
                        span('The following movies are missing key data.', cls='title')
                        br()
                        span('Please fill out or correct IMDB ID and resolution, or uncheck to ignore.', cls='title')
                        table(id='missing_data')
                    with span(id='import'):
                        i(cls='fa fa-check-circle')
                        span('Import')
                with div(id='results'):

                    with a(id='finished', href='{}/status'.format(core.URL_BASE)):
                        i(cls='fa fa-thumbs-o-up')
                        span('Cool')

                div(id='thinker')
        return doc.render()

# pylama:ignore=W0401
