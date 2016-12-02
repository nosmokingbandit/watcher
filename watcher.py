import os
import sys
import cherrypy
import datetime
import core
from core import poster, sqldb, config, ajax, api, version
from core.scheduler import SchedulerPlugin
from core.log import log
import argparse, time
from cherrypy.process.plugins import Daemonizer
import webbrowser
from templates import status, add_movie, settings, restart, shutdown, update

core.PROG_PATH = os.path.dirname(os.path.realpath(__file__))
os.chdir(core.PROG_PATH)

class App(object):
    @cherrypy.expose
    def __init__(self):
        self.ajax = ajax.Ajax()

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/status")

    '''
    From here down just forward requests to ajax.Ajax()
    '''
    @cherrypy.expose
    def search_omdb(self, search_term):
        return self.ajax.search_omdb(search_term)

    @cherrypy.expose
    def add_wanted_movie(self, data):
        return self.ajax.add_wanted_movie(data)

    @cherrypy.expose
    def manual_download(self, guid):
        return self.ajax.manual_download(guid)

    @cherrypy.expose
    def mark_bad(self, guid):
        return self.ajax.mark_bad(guid)

    @cherrypy.expose
    def movie_info_popup(self, imdbid):
        return self.ajax.movie_info_popup(imdbid)

    @cherrypy.expose
    def movie_status_popup(self, imdbid):
        return self.ajax.movie_status_popup(imdbid)

    @cherrypy.expose
    def refresh_list(self, list, imdbid=''):
        return self.ajax.refresh_list(list, imdbid)

    @cherrypy.expose
    def remove_movie(self, imdbid):
        return self.ajax.remove_movie(imdbid)

    @cherrypy.expose
    def server_status(self, mode):
        return self.ajax.server_status(mode)

    @cherrypy.expose
    def save_settings(self, data):
        return self.ajax.save_settings(data)

    @cherrypy.expose
    def search(self, imdbid, title):
        return self.ajax.search(imdbid, title)

    @cherrypy.expose
    def test_downloader_connection(self, mode, data):
        return self.ajax.test_downloader_connection(mode, data)

    @cherrypy.expose
    def update_now(self, mode):
        '''
        Executes update method from version.Version()

        The ajax response is a generator that will contain only the success/fail message.

        We do this so the message can be passed to the ajax request in the browser while cherrypy restarts.
        '''

        response = self.ajax.update_now(mode)
        for i in response:
            return i

    @cherrypy.expose
    def update_quality_settings(self, quality, imdbid):
        return self.ajax.update_quality_settings(quality, imdbid)

if __name__ == '__main__':

    # parse user-passed arguments
    parser = argparse.ArgumentParser(description="Watcher Server App")
    parser.add_argument('-d','--daemon',help='Run the server as a daemon.', action='store_true')
    parser.add_argument('-a','--bind-address',help='Network address to bind to.')
    parser.add_argument('-p','--port',help='Port to bind to.', type=int)
    parser.add_argument('-b','--browser', help='Open browser on launch.',action='store_true')
    parser.add_argument('--conf', help='Location of config file.', type=str)
    passed_args = parser.parse_args()


    if passed_args.conf:
        core.CONF_FILE = passed_args.conf

    # set up config file on first launch
    conf = config.Config()
    if not os.path.isfile(core.CONF_FILE):
        print 'Config file not found. Creating new basic config {}. Please review settings.'.format(core.CONF_FILE)
        conf.new_config()
    else:
        print 'Config file found, merging any new options.'
        conf.merge_new_options()
    conf.stash()

    # set up logging now that the config is ready
    log.start()
    import logging
    logging = logging.getLogger(__name__)

    # set up db on first launch
    sql = sqldb.SQL()
    if not os.path.isfile('watcher.sqlite'):
        logging.info('SQL DB not found. Creating.')
        sql = sqldb.SQL()
        sql.create_database()
    else:
        logging.info('SQL DB found.')
        print 'Database found, altering if necessary.'
        sql.add_new_columns()
    del sql

    # Get server settings ready
    server_conf = core.CONFIG['Server']
    conf_port = server_conf['serverport']
    conf_host = server_conf['serverhost']
    conf_browser = server_conf['launchbrowser']

    if passed_args.bind_address:
        core.SERVER_ADDRESS = passed_args.bind_address
    else:
        core.SERVER_ADDRESS = conf_host

    if passed_args.port:
        core.SERVER_PORT = passed_args.port
    else:
        core.SERVER_PORT = int(conf_port)

    # Set up base cherrypy config
    cherry_conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': core.PROG_PATH
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }

    # update global cherrypy configs
    cherrypy.config.update({
        'engine.autoreload.on': False,
        'server.socket_host': core.SERVER_ADDRESS,
        'server.socket_port': core.SERVER_PORT
    })

    # enable all cherrypy logging
    cherrypy.log.error_log.propagate = True
    cherrypy.log.access_log.propagate = True

    # start up scheduler plugin
    scheduler = SchedulerPlugin(cherrypy.engine)

    # assign page urls
    root = App()
    root.add_movie = add_movie.AddMovie()
    root.status = status.Status()
    root.settings = settings.Settings()
    root.restart = restart.Restart()
    root.shutdown = shutdown.Shutdown()
    root.update = update.Update()

    # daemonize if desired
    if passed_args.daemon:
        Daemonizer(cherrypy.engine).subscribe()

    # mount applications
    cherrypy.tree.mount(root,
                        '/',
                        cherry_conf
                       )

    cherrypy.tree.mount(api.API(),
                        '/api',
                        api.API.conf
                       )

    # if everything goes well so far, open the browser
    if passed_args.browser or conf_browser == True:
        webbrowser.open( "http://{}:{}".format(core.SERVER_ADDRESS,core.SERVER_PORT) )
        logging.info('Launching web browser.')


    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()
    # have to do this for the daemon
    os.chdir(core.PROG_PATH)
    scheduler.subscribe()
    scheduler.start()

    cherrypy.engine.block()
