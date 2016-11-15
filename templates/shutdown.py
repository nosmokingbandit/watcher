import dominate
from dominate.tags import *
from header import Header
from cherrypy import expose


class Shutdown():

    @expose
    def index(self):
        doc = dominate.document(title='Watcher')

        with doc.head:
            base(href="/static/")

            link(rel='stylesheet', href='css/style.css')
            link(rel='stylesheet', href='css/shutdown.css')
            link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')

            script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js')
            script(type='text/javascript', src='js/shutdown/main.js')


        with doc:
            with div(id='content'):
                div(id='thinker')
                span('Shutting Down', cls='msg')

        return doc.render()
