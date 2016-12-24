import dominate
from cherrypy import expose
from dominate.tags import *
from head import Head

class Restart():

    @expose
    def index(self):
        doc = dominate.document(title='Watcher')

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href='static/css/restart.css')
            script(type='text/javascript', src='static/js/restart/main.js')

        with doc:
            with div(id='content'):
                div(id='thinker')
                span('Restarting', cls='msg')
                with span('Timeout Exceeded.', cls='error'):
                    p('Watcher is taking too long to restart, please check your logs and restart manually.')

        return doc.render()
