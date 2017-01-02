import cherrypy
import core
import dominate
from cherrypy import expose
from dominate.tags import *
from head import Head


class Update():

    @expose
        if not core.UPDATING:
            raise cherrypy.HTTPRedirect(core.URL_BASE + '/status')
            return
    def default(self):

        doc = dominate.document(title='Watcher')

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/update.css')
            script(type='text/javascript', src=core.URL_BASE + '/static/js/update/main.js?v=12.27')

        with doc:
            with div(id='content'):
                div(id='thinker')
                span('Updating', cls='msg')

        return doc.render()
