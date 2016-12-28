import dominate
import core
from cherrypy import expose
from dominate.tags import *

class Login(object):

    def __init__(self):
        return

    @expose
    def index(self, username=None, from_page=''):
        if username == None:
            username = ''

        doc = dominate.document(title='Watcher')

        with doc.head:
            link(rel='stylesheet', href='static/css/style.css')
            link(rel='stylesheet', href='static/css/login.css')
            link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')
            link(rel='stylesheet', href='static/font-awesome/css/font-awesome.css')

        with doc:
            with div(id='content'):
                img(src='static/images/logo.png', id='logo')
                br()
                with form(method='post', action='login', id='login_form'):
                    input(type='text', name='username', placeholder='Username', value=username)
                    br()
                    input(type='password', name='password', placeholder='Password')
                    br()
                    with button(type='submit', value='Enter'):
                        i(cls='fa fa-sign-in')



        return doc.render()
