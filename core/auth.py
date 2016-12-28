import cherrypy
import core
from templates import login

## TODO add logging

SESSION_KEY = '_cp_username'


def check_credentials(username, password):
    ''' Verifies credentials for username and password.
    :param username: str name to check against config
    :param password: str password to check against config


    Returns None on success or a string describing the error on failure
    '''

    if username == core.CONFIG['Server']['authuser'] and password == core.CONFIG['Server']['authpass']:
        return None
    else:
        return u"Incorrect username or password."


def check_auth(*args, **kwargs):

    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise cherrypy.HTTPRedirect(core.URL_BASE + "/auth/login")
        else:
            raise cherrypy.HTTPRedirect(core.URL_BASE + "/auth/login")


cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)


def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate


# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
#
# They can access the current username as cherrypy.request.login
#
# Define those at will however suits the application.

def member_of(groupname):
    def check():
        # replace with actual check if <username> is in <groupname>
        return cherrypy.request.login == 'joe' and groupname == 'admin'
    return check


def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login

# These might be handy


def any_of(*conditions):
    """Returns True if any of the conditions match"""
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check


# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
    """Returns True if all of the conditions match"""
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check


# Controller to provide login and logout actions

class AuthController(object):

    def __init__(self):
        self.login_form = login.Login()

        self.conf = {
                '/': {
                    'tools.sessions.on': True,
                    'tools.sessions.timeout': 60,
                    'tools.staticdir.root': core.PROG_PATH
                },
                '/static': {
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': './static'
                }
            }

    def on_login(self, username):
        """Called on successful login"""

    def on_logout(self, username):
        """Called on logout"""

    def get_loginform(self, username, msg="Enter login information", from_page="/"):
        return self.login_form.index(username=username, from_page=from_page)
        # """<html>
        #     <body>
        #     <form method="post" action="login">
        #     <input type="hidden" name="from_page" value="%(from_page)s" />
        #     %(msg)s<br />
        #     Username: <input type="text" name="username" value="%(username)s" /><br />
        #     Password: <input type="password" name="password" /><br />
        #     <input type="submit" value="Log in" />
        # </body></html>""" % locals()

    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):
        if username is None or password is None:
            return self.login_form.index(username=username, from_page=from_page)

        error_msg = check_credentials(username, password)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            try:
                cherrypy.session.regenerate()
            except Exception, e:
                pass
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect(core.URL_BASE + '/')

    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(core.URL_BASE + '/')
