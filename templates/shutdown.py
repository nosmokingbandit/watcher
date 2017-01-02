import dominate
import core
from cherrypy import expose
from dominate.tags import *
from head import Head
from core import config

class Shutdown():

    @expose
    def default(self):
        doc = dominate.document(title='Watcher')
        theme=str(core.CONFIG['Server']['csstheme']
                  
        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/' + theme + '/shutdown.css')
            script(type='text/javascript', src=core.URL_BASE + '/static/js/shutdown/main.js?v=12.27')

        with doc:
            with div(id='content'):
                div(id='thinker')
                span('Shutting Down', cls='msg')

        return doc.render()
