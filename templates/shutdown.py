import dominate
from cherrypy import expose
from dominate.tags import *
from head import Head


class Shutdown():

    @expose
    def index(self):
        doc = dominate.document(title='Watcher')

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href='static/css/shutdown.css')
            script(type='text/javascript', src='static/js/shutdown/main.js')

        with doc:
            with div(id='content'):
                div(id='thinker')
                span('Shutting Down', cls='msg')

        return doc.render()
