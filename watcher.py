import os
import sys
lib_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
sys.path.append(lib_dir)

import argparse
import datetime
import logging
import os
import webbrowser

import cherrypy
import core
from cherrypy.process.plugins import Daemonizer
from core import ajax, api, config, postprocessing, searcher, sqldb
from core.log import log
from core.notification import Notification
from core.scheduler import Scheduler
from templates import add_movie, restart, settings, shutdown, status, update, fourohfour

if os.name == 'nt':
    from core.plugins import systray

core.PROG_PATH = os.path.dirname(os.path.realpath(__file__))
os.chdir(core.PROG_PATH)


class App(object):
    @cherrypy.expose
    def __init__(self):
        self.ajax = ajax.Ajax()
        self.conf = {
                '/': {
                    'tools.sessions.on': True,
                    #'tools.auth.on': False,
                    'tools.staticdir.root': core.PROG_PATH
                },
                '/static': {  # # use mount variable here?
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': './static'
                }
            }

        # point server toward custom 404
        cherrypy.config.update({
            'error_page.404': self.error_page_404
        })
        return

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("status")

    @cherrypy.expose
    def error_page_404(self, *args, **kwargs):
        return fourohfour.FourOhFour.index()


if __name__ == '__main__':

    # parse user-passed arguments
    parser = argparse.ArgumentParser(description="Watcher Server App")
    parser.add_argument('-d', '--daemon', help='Run the server as a daemon.',
                        action='store_true')
    parser.add_argument('-a', '--address', help='Network address to bind to.')
    parser.add_argument('-p', '--port', help='Port to bind to.', type=int)
    parser.add_argument('-b', '--browser', help='Open browser on launch.',
                        action='store_true')
    parser.add_argument('-c', '--conf', help='Location of config file.',
                        type=str)
    parser.add_argument('-l', '--log',
                        help='Directory in which to create log files.', type=str)
    passed_args = parser.parse_args()

    # Set up conf file
    if passed_args.conf:
        core.CONF_FILE = passed_args.conf
    if passed_args.log:
        core.LOG_DIR = passed_args.log

    # set up config file on first launch
    conf = config.Config()
    if not os.path.isfile(core.CONF_FILE):
        print 'Config file not found. Creating new basic config {}. ' \
            'Please review settings.'.format(core.CONF_FILE)
        conf.new_config()
    else:
        print 'Config file found, merging any new options.'
        conf.merge_new_options()
    conf.stash()

    # Set up logging
    if passed_args.log:
        core.LOG_DIR = passed_args.log
    log.start(core.LOG_DIR)
    logging = logging.getLogger(__name__)
    cherrypy.log.error_log.propagate = True
    cherrypy.log.access_log.propagate = True

    # Set up server
    if passed_args.address:
        core.SERVER_ADDRESS = passed_args.address
    else:
        core.SERVER_ADDRESS = str(core.CONFIG['Server']['serverhost'])
    if passed_args.port:
        core.SERVER_PORT = passed_args.port
    else:
        core.SERVER_PORT = int(core.CONFIG['Server']['serverport'])

    # update cherrypy config based on passed args
    cherrypy.config.update({
        'engine.autoreload.on': False,
        'server.socket_host': core.SERVER_ADDRESS,
        'server.socket_port': core.SERVER_PORT
    })

    # set up db on first launch
    sql = sqldb.SQL()
    if not os.path.isfile('watcher.sqlite'):
        logging.info('SQL DB not found. Creating.')
        sql = sqldb.SQL()
        sql.create_database()
    else:
        logging.info('SQL DB found.')
        print 'Database found.'
    del sql

    root = App()
    root.add_movie = add_movie.AddMovie()
    root.status = status.Status()
    root.settings = settings.Settings()
    root.restart = restart.Restart()
    root.shutdown = shutdown.Shutdown()
    root.update = update.Update()

    # Set up root app
    if core.CONFIG['Server']['behindproxy'] == 'true':
        core.URL_BASE = '/watcher'

    # mount applications
    cherrypy.tree.mount(root,
                        '{}/'.format(core.URL_BASE),
                        root.conf
                        )

    cherrypy.tree.mount(api.API(),
                        '{}/api'.format(core.URL_BASE),
                        api.API.conf
                        )

    cherrypy.tree.mount(postprocessing.Postprocessing(),
                        '{}/postprocessing'.format(core.URL_BASE),
                        postprocessing.Postprocessing.conf
                        )

    # if everything goes well so far, open the browser
    if passed_args.browser or core.CONFIG['Server']['launchbrowser'] == 'true':
        webbrowser.open("http://{}:{}{}".format(
            core.SERVER_ADDRESS, core.SERVER_PORT, core.URL_BASE))
        logging.info('Launching web browser.')

    # daemonize in *nix if desired
    if passed_args.daemon and os.name == 'posix':
        Daemonizer(cherrypy.engine).subscribe()

    # start engine
    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()

    # Create plugin instances and subscribe
    scheduler = Scheduler()
    scheduler.AutoSearch.create()
    scheduler.AutoUpdateCheck.create()
    scheduler.AutoUpdateInstall.create()
    scheduler.plugin.subscribe()

    # If windows os and daemon selected, start systray
    if passed_args.daemon and os.name == 'nt':
        systrayplugin = systray.SysTrayPlugin(cherrypy.engine)
        systrayplugin.subscribe()
        systrayplugin.start()

    os.chdir(core.PROG_PATH)  # have to do this for the daemon
    # finish by blocking
    cherrypy.engine.block()
