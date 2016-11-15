import os
import cherrypy
import datetime
from core import search_omdb, poster, sqldb, config, ajax, api
from core.scheduler import SchedulerPlugin
from core.log import log
import argparse, time
from cherrypy.process.plugins import Daemonizer
import webbrowser
from templates import status, add_movie, settings, restart, shutdown

cwd = os.getcwd()

class App(object):
    @cherrypy.expose
    def __init__(self):
        self.ajax = ajax.Ajax()

        if not os.path.isfile('config.cfg'):
            logging.info('Config file not found. Creating new basic config. Please review settings.')
            conf.new_config()
        else:
            logging.info('Config file found.')

        if not os.path.isfile('watcher.sqlite'):
            logging.info('SQL DB not found. Creating.')
            sql = sqldb.SQL()
            sql.create_database()
            del sql
        else:
            logging.info('SQL DB found.')


    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/status")

    # Ajax Requests
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
    def search_all(self, purge=False):
        return self.ajax.search_all(purge=purge)

    @cherrypy.expose
    def test_downloader_connection(self, mode, data):
        return self.ajax.test_downloader_connection(mode, data)

if __name__ == '__main__':
    # set up logging
    log.start()
    import logging
    logging = logging.getLogger(__name__)


    conf = config.Config()
    scheduler = SchedulerPlugin(cherrypy.engine)

    cherry_conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(cwd)
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }

    server_conf = conf['Server']
    conf_port = server_conf['serverport']
    conf_host = server_conf['serverhost']
    conf_browser = server_conf['launchbrowser']

    parser = argparse.ArgumentParser(description="Watcher Server App")
    parser.add_argument('-d','--daemon',help='Run the server as a daemon.',action='store_true')
    parser.add_argument('-a','--bind-address',help='Network interface to bind to.',default=conf_host)
    parser.add_argument('-p','--port',help='Port to bind to.',default=conf_port, type=int)
    parser.add_argument('-b','--browser', help='Open browser on launch.',action='store_true')
    passed_args = parser.parse_args()

    cherrypy.config.update({
        'server.socket_host':passed_args.bind_address,
        'server.socket_port':passed_args.port
    })

    if passed_args.browser or conf_browser == True:
        webbrowser.open( "http://{}:{}".format(passed_args.bind_address,passed_args.port) )
        logging.info('Launching web browser.')

    cherrypy.log.error_log.propagate = True
    cherrypy.log.access_log.propagate = True

    #log.rotate_logs()

    root = App()
    root.add_movie = add_movie.AddMovie()
    root.status = status.Status()
    root.settings = settings.Settings()
    root.restart = restart.Restart()
    root.shutdown = shutdown.Shutdown()

    if passed_args.daemon:
        Daemonizer(cherrypy.engine).subscribe()



    cherrypy.tree.mount(root,
                        '/',
                        cherry_conf
                       )

    cherrypy.tree.mount(api.API(),
                        '/api',
                        api.API.conf
                       )
    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()
    os.chdir(cwd) # have to do this for the daemon
    scheduler.subscribe()
    scheduler.start()
    cherrypy.engine.block()
