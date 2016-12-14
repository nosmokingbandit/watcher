import sys
sys.path.append('lib')
import argparse
import cherrypy
from cherrypy.process.plugins import Daemonizer
import datetime
import os
import webbrowser
import core
from core import sqldb, config, ajax, api, postprocessing, searcher
from core.log import log
from core.plugins import taskscheduler
from templates import status, add_movie, settings, restart, shutdown, update

if os.name == 'nt':
    from core.plugins import systray

core.PROG_PATH = os.path.dirname(os.path.realpath(__file__))
os.chdir(core.PROG_PATH)


class App(object):
    @cherrypy.expose
    def __init__(self):
        self.ajax = ajax.Ajax()
        # point server toward custom 404
        cherrypy.config.update({
            'error_page.404': self.error_page_404
        })

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/status")

    @cherrypy.expose
    def error_page_404(self, *args, **kwargs):
        # TODO: this should be prettier
        return "Page not Found!"

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
    def mark_bad(self, guid, imdbid):
        return self.ajax.mark_bad(guid, imdbid)

    @cherrypy.expose
    def movie_info_popup(self, imdbid):
        return self.ajax.movie_info_popup(imdbid)

    @cherrypy.expose
    def movie_status_popup(self, imdbid):
        return self.ajax.movie_status_popup(imdbid)

    @cherrypy.expose
    def quick_add(self, imdbid):
        return self.ajax.quick_add(imdbid)

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
        ''' Executes update method from version.Version()

        The ajax response is a generator that will contain
            only the success/fail message.

        This is done so the message can be passed to the ajax
            request in the browser while cherrypy restarts.
        '''

        response = self.ajax.update_now(mode)
        for i in response:
            return i

    @cherrypy.expose
    def update_quality_settings(self, quality, imdbid):
        return self.ajax.update_quality_settings(quality, imdbid)


class Scheduler(object):

    def __init__(self):
        # create scheduler plugin
        self.plugin = taskscheduler.SchedulerPlugin(cherrypy.engine)

    #create classes for each scheduled task
    class AutoSearch(object):
        @staticmethod
        def create():
            search = searcher.Searcher()
            interval = int(core.CONFIG['Search']['searchfrequency']) * 3600

            hr = int(core.CONFIG['Search']['searchtimehr'])
            min = int(core.CONFIG['Search']['searchtimemin'])

            task_search = taskscheduler.ScheduledTask(hr, min, interval,
                search.auto_search_and_grab, auto_start=True)
            delay = task_search.task.delay

            now = datetime.datetime.today().replace(second=0, microsecond=0)
            core.NEXT_SEARCH = now + datetime.timedelta(0, delay)

    class AutoUpdate(object):

        def __init__(self):
            return

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
    import logging
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
        print 'Database found, altering if necessary.'
        sql.add_new_columns()
        sql.convert_movies()
    del sql

    # Set up root app
    root = App()
    root.add_movie = add_movie.AddMovie()
    root.status = status.Status()
    root.settings = settings.Settings()
    root.restart = restart.Restart()
    root.shutdown = shutdown.Shutdown()
    root.update = update.Update()

    # mount applications
    cherrypy.tree.mount(root,
                        '/',
                        cherry_conf
                       )

    cherrypy.tree.mount(api.API(),
                        '/api',
                        api.API.conf
                       )

    cherrypy.tree.mount(postprocessing.Postprocessing(),
                        '/postprocessing',
                        postprocessing.Postprocessing.conf
                       )

    # if everything goes well so far, open the browser
    if passed_args.browser or core.CONFIG['Server']['launchbrowser'] == 'true':
        webbrowser.open("http://{}:{}".format(
            core.SERVER_ADDRESS, core.SERVER_PORT))
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
    scheduler.plugin.subscribe()

    # If windows os and daemon selected, start systray
    if passed_args.daemon and os.name == 'nt':
        systrayplugin = systray.SysTrayPlugin(cherrypy.engine)
        systrayplugin.subscribe()
        systrayplugin.start()

    # finish by blocking
    os.chdir(core.PROG_PATH) # have to do this for the daemon
    cherrypy.engine.block()
