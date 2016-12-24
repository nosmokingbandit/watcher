import dominate
import core
from core import config
from cherrypy import expose
from dominate.tags import *


class FourOhFour():

    @staticmethod
    @expose
    def index():

        theme=str(core.CONFIG['Server']['csstheme'])

        doc = dominate.document(title='Watcher')

        with doc.head:
            base(href="/static/")

            link(rel='stylesheet', href='css/'+theme+'/style.css')
            link(rel='stylesheet', href='css/'+theme+'/fourohfour.css')
            link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')

        with doc:
            with div(id='content'):
                with span(cls='msg'):
                    span('404')
                    br()
                    span('Page Not Found')

        return doc.render()
