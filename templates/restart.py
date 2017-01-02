import dominate
import core
from cherrypy import expose
from dominate.tags import *
from head import Head
from core import config

class Restart():

    @expose
    def default(self):
        doc = dominate.document(title='Watcher')
        theme=str(core.CONFIG['Server']['csstheme'])
        
        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/' + theme + '/restart.css')
            script(type='text/javascript', src=core.URL_BASE + '/static/js/restart/main.js?v=12.27')

        with doc:
            with div(id='content'):
                div(id='thinker')
                span('Restarting', cls='msg')
                with span('Timeout Exceeded.', cls='error'):
                    p('Watcher is taking too long to restart, please check your logs and restart manually.')

        return doc.render()
