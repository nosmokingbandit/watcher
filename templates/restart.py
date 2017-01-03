import dominate
import core
from cherrypy import expose
from dominate.tags import *
from head import Head


class Restart():

    @expose
    def default(self):
        doc = dominate.document(title='Watcher')

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/restart.css')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/restart.css'.format(core.THEME))
            script(type='text/javascript', src=core.URL_BASE + '/static/js/restart/main.js?v=12.27')

        with doc:
            with div(id='content'):
                div(id='thinker')
                span('Restarting', cls='msg')
                with span('Timeout Exceeded.', cls='error'):
                    p('Watcher is taking too long to restart, please check your logs and restart manually.')

        return doc.render()
