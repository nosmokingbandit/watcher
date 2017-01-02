import dominate
import core
from cherrypy import expose
from dominate.tags import *
from head import Head
from core import config

class FourOhFour():

    @staticmethod
    @expose
    def default():

        doc = dominate.document(title='Watcher')
        theme=str(core.CONFIG['Server']['csstheme'])
        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/' + theme + '/fourohfour.css')
            style

        with doc:
            with div(id='content'):
                with span(cls='msg'):
                    span('404')
                    br()
                    span('Page Not Found')

        return doc.render()
