import dominate
import core
from core import config
from cherrypy import expose
from dominate.tags import *


class Restart():

    @expose
    def index(self):
	theme=str(core.CONFIG['Server']['csstheme'])
		
        doc = dominate.document(title='Watcher')

        with doc.head:
            base(href="/static/")

            link(rel='stylesheet', href='css/'+theme+'/style.css')
            link(rel='stylesheet', href='css/'+theme+'/restart.css')
            link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')

            script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js')
            script(type='text/javascript', src='js/restart/main.js')

        with doc:
            with div(id='content'):
                div(id='thinker')
                span('Restarting', cls='msg')
                with span('Timeout Exceeded.', cls='error'):
                    p('Watcher is taking too long to restart, please check your logs and restart manually.')

        return doc.render()
