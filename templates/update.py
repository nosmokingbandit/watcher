import dominate
from dominate.tags import *
from cherrypy import expose
import core
import cherrypy


class Update():

    @expose
    def index(self):
        if not core.UPDATING:
            raise cherrypy.HTTPRedirect("/status")
            return

        doc = dominate.document(title='Watcher')

        with doc.head:
            base(href="/static/")

            link(rel='stylesheet', href='css/style.css')
            link(rel='stylesheet', href='css/update.css')
            link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')

            script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js')
            script(type='text/javascript', src='js/update/main.js')

        with doc:
            with div(id='content'):
                div(id='thinker')
                span('Updating', cls='msg')

        return doc.render()
