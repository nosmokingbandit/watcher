import datetime

import cherrypy
import core

from core import searcher, version
from core.plugins import taskscheduler

class Scheduler(object):

    def __init__(self):
        # create scheduler plugin
        self.plugin = taskscheduler.SchedulerPlugin(cherrypy.engine)
        self.version = version.Version()

    # create classes for each scheduled task
    class AutoSearch(object):
        @staticmethod
        def create():
            search = searcher.Searcher()
            interval = int(core.CONFIG['Search']['searchfrequency']) * 3600

            hr = int(core.CONFIG['Search']['searchtimehr'])
            min = int(core.CONFIG['Search']['searchtimemin'])

            task_search = taskscheduler.ScheduledTask(hr, min, interval,
                          search.auto_search_and_grab, auto_start=True)

            # update core.NEXT_SEARCH
            delay = task_search.task.delay
            now = datetime.datetime.today().replace(second=0, microsecond=0)
            core.NEXT_SEARCH = now + datetime.timedelta(0, delay)

    class AutoUpdateCheck(object):

        @staticmethod
        def create():

            interval = int(core.CONFIG['Server']['checkupdatefrequency']) * 3600

            now = datetime.datetime.today()
            hr = now.hour
            min = now.minute
            if now.second > 30:
                min += 1

            if core.CONFIG['Server']['checkupdates'] == 'true':
                auto_start = True
            else:
                auto_start = False

            taskscheduler.ScheduledTask(hr, min, interval, Scheduler.AutoUpdateCheck.update_check,
                                        auto_start=auto_start)
            return

        @staticmethod
        def update_check():
            ''' Checks for any available updates

            Returns dict from core.version.Version.manager.update_check():
                {'status': 'error', 'error': <error> }
                {'status': 'behind', 'behind_count': #, 'local_hash': 'abcdefg', 'new_hash': 'bcdefgh'}
                {'status': 'current'}
            '''

            data = Scheduler.version.manager.update_check()
            # if data['status'] == 'current', nothing to do.

            if data['status'] == 'error':
                notif = {'icon': 'fa-exclamation-triangle',
                         'title': 'Error Checking for Updates',
                         'text': data['error']
                         }
                Notification.add(notif)


            elif data['status'] == 'behind':
                if core.CONFIG['Server']['installupdates'] == 'true':
                    hour = core.CONFIG['Server']['installupdatehr']
                    minute = core.CONFIG['Server']['installupdatemin']
                    text = 'Updates will install automatically at {}:{}'.format(hour, minute)
                else:
                    text = None

                title_link = '{}/compare/{}...{}'.format(core.GIT_API, data['new_hash'], data['local_hash'])

                button = ('Update Now', '/update_now', 'fa-arrow-circle-up')

                notif = {'icon': 'fa-star',
                         'title': '{} Updates Available'.format(data['behind_count']),
                         'title_link': title_link,
                         'text': text,
                         'button': button}
                Notification.add(notif)

            return data

    class AutoUpdateInstall(object):

        @staticmethod
        def create():
            interval = 24 * 3600

            hr = int(core.CONFIG['Server']['installupdatehr'])
            min = int(core.CONFIG['Server']['installupdatemin'])

            if core.CONFIG['Server']['installupdates'] == 'true':
                auto_start = True
            else:
                auto_start = False

            taskscheduler.ScheduledTask(hr, min, interval, Scheduler.AutoUpdateInstall.install,
                                        auto_start=auto_start)
            return

        @staticmethod
        def install():
            ver = version.Version()

            if not core.UPDATE_STATUS or core.UPDATE_STATUS['status'] != 'behind':
                return

            logging.info('Running automatic updater.')

            logging.info('Currently {} commits behind. Updating to {}.'.format(
                         core.UPDATE_STATUS['behind_count'], core.UPDATE_STATUS['new_hash']))

            core.UPDATING = True

            logging.info('Executing update.')
            update = Scheduler.version.manager.execute_update()
            core.UPDATING = False

            if not update:
                logging.error('Update failed.')

            logging.info('Update successful, restarting.')
            cherrypy.engine.restart()
            return
