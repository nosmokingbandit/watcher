import dominate
from cherrypy import expose
from dominate.tags import *


class FourOhFour():

    @staticmethod
    @expose
    def index():

        doc = dominate.document(title='Watcher')

        with doc.head:
            base(href="/static/")

            link(rel='stylesheet', href='css/style.css')
            link(rel='stylesheet', href='css/fourohfour.css')
            link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')

        with doc:
            with div(id='content'):
                with span(cls='msg'):
                    span('404')
                    br()
                    span('Page Not Found')

        return doc.render()
