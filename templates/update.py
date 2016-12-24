import cherrypy
import core
import dominate
from cherrypy import expose
from dominate.tags import *
from head import Head


class Update():

    @expose
    def index(self):
        if not core.UPDATING:
            raise cherrypy.HTTPRedirect("/status")
            return

        doc = dominate.document(title='Watcher')

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href='static/css/update.css')
            script(type='text/javascript', src='static/js/update/main.js')

        with doc:
            with div(id='content'):
                div(id='thinker')
                span('Updating', cls='msg')

        return doc.render()
