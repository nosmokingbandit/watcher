#!/usr/bin/env python

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))

import argparse
import datetime
import logging
import os
import webbrowser
import ssl
import cherrypy
import core
from cherrypy.process.plugins import Daemonizer, PIDFile
from core import ajax, api, config, postprocessing, scheduler, searcher, sqldb, version
from core.auth import AuthController, require
from core.log import log
from core.notification import Notification
from templates import add_movie, restart, settings, shutdown, status, update, fourohfour

if os.name == 'nt':
    from core.plugins import systray

core.PROG_PATH = os.path.dirname(os.path.realpath(__file__))
os.chdir(core.PROG_PATH)


class App(object):

    auth = AuthController()

    @cherrypy.expose
    def __init__(self):
        if core.CONFIG['Server']['authrequired'] == 'true':
            self._cp_config = {
                'auth.require': []
            }

        self.ajax = ajax.Ajax()
        self.add_movie = add_movie.AddMovie()
        self.status = status.Status()
        self.settings = settings.Settings()
        self.restart = restart.Restart()
        self.shutdown = shutdown.Shutdown()
        self.update = update.Update()

        # point server toward custom 404
        cherrypy.config.update({
            'error_page.404': self.error_page_404
        })

        if core.CONFIG['Server']['checkupdates'] == 'true':
            scheduler.AutoUpdateCheck.update_check()

        return

    @cherrypy.expose
    def default(self):
        raise cherrypy.InternalRedirect('/status/')

    @cherrypy.expose
    def error_page_404(self, *args, **kwargs):
        return fourohfour.FourOhFour.default()


if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context

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
    parser.add_argument('--db',
                        help='Absolute path to database file.', type=str)
    parser.add_argument('--pid',
                        help='Directory in which to store pid file.', type=str)
    passed_args = parser.parse_args()

    if passed_args.pid:
        PIDFile(cherrypy.engine, passed_args.pid).subscribe()

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
    # apply theme
    core.THEME = core.CONFIG['Server']['theme']

    # Set up logging
    if passed_args.log:
        core.LOG_DIR = passed_args.log
    log.start(core.LOG_DIR)
    logging = logging.getLogger(__name__)
    cherrypy.log.error_log.propagate = True
    cherrypy.log.access_log.propagate = False

    # Set up server
    if passed_args.address:
        core.SERVER_ADDRESS = passed_args.address
    else:
        core.SERVER_ADDRESS = str(core.CONFIG['Server']['serverhost'])
    if passed_args.port:
        core.SERVER_PORT = passed_args.port
    else:
        core.SERVER_PORT = int(core.CONFIG['Server']['serverport'])

    # set up db on first launch
    if passed_args.db:
        core.DB_FILE = passed_args.db
    sql = sqldb.SQL()
    if not os.path.isfile('watcher.sqlite'):
        logging.info('SQL DB not found. Creating.')
        sql = sqldb.SQL()
        sql.create_database()
    else:
        logging.info('SQL DB found.')
        print 'Database found.'
    del sql

    # mount and configure applications
    if core.CONFIG['Proxy']['behindproxy'] == 'true':
        core.URL_BASE = core.CONFIG['Proxy']['webroot']
    root = cherrypy.tree.mount(App(),
                               '{}/'.format(core.URL_BASE),
                               'core/conf_app.ini'
                               )
    cherrypy.tree.mount(api.API(),
                        '{}/api'.format(core.URL_BASE),
                        'core/conf_api.ini'
                        )

    cherrypy.tree.mount(postprocessing.Postprocessing(),
                        '{}/postprocessing'.format(core.URL_BASE),
                        'core/conf_postprocessing.ini'
                        )

    cherrypy.tree.mount(App.auth,
                        '{}/auth'.format(core.URL_BASE),
                        'core/conf_auth.ini'
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
    cherrypy.config.update('core/conf_global.ini')
    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()

    # Create plugin instances and subscribe
    scheduler_plugin = scheduler.Scheduler()
    scheduler.AutoSearch.create()
    scheduler.AutoUpdateCheck.create()
    scheduler.AutoUpdateInstall.create()
    scheduler_plugin.plugin.subscribe()

    # If windows os and daemon selected, start systray
    if passed_args.daemon and os.name == 'nt':
        systrayplugin = systray.SysTrayPlugin(cherrypy.engine)
        systrayplugin.subscribe()
        systrayplugin.start()

    os.chdir(core.PROG_PATH)  # have to do this for the daemon
    # finish by blocking
    cherrypy.engine.block()
