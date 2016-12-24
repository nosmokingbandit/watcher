import cherrypy
import core
import dominate
from core import config
from cherrypy import expose
from dominate.tags import *


class Update():

    @expose
    def index(self):
        if not core.UPDATING:
            raise cherrypy.HTTPRedirect("/status")
            return

	theme=str(core.CONFIG['Server']['csstheme'])
		
        doc = dominate.document(title='Watcher')

        with doc.head:
            base(href="/static/")

            link(rel='stylesheet', href='css/'+theme+'/style.css')
            link(rel='stylesheet', href='css/'+theme+'/update.css')
            link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')

            script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js')
            script(type='text/javascript', src='js/update/main.js')

        with doc:
            with div(id='content'):
                div(id='thinker')
                span('Updating', cls='msg')

        return doc.render()
