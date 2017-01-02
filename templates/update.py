import cherrypy
import core
import dominate
from cherrypy import expose
from dominate.tags import *
from head import Head


class Update():

    @expose
    def default(self):
        if core.UPDATING:
            updating = 'true'
        else:
            updating = 'false'

        doc = dominate.document(title='Watcher')

        with doc.head:
            meta(name='updating', content=updating)
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/update.css')
            script(type='text/javascript', src=core.URL_BASE + '/static/js/update/main.js?v=01.01')

        with doc:
            with div(id='content'):
                div(id='thinker')
                span('Updating', cls='msg')

        return doc.render()
