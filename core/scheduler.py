import datetime

import cherrypy
import core
from core.notification import Notification

from core import searcher, version
from core.plugins import taskscheduler


class Scheduler(object):

    def __init__(self):
        # create scheduler plugin
        self.plugin = taskscheduler.SchedulerPlugin(cherrypy.engine)

# create classes for each scheduled task
class AutoSearch(object):
    @staticmethod
    def create():
        search = searcher.Searcher()
        interval = int(core.CONFIG['Search']['searchfrequency']) * 3600

        hr = int(core.CONFIG['Search']['searchtimehr'])
        min = int(core.CONFIG['Search']['searchtimemin'])

        task_search = taskscheduler.ScheduledTask(hr, min, interval,
                                                  search.auto_search_and_grab,
                                                  auto_start=True)

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

        taskscheduler.ScheduledTask(hr, min, interval, AutoUpdateCheck.update_check,
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

        ver = version.Version()

        data = ver.manager.update_check()
        # if data['status'] == 'current', nothing to do.

        if data['status'] == 'error':
            notif = {'type': 'error',
                     'title': 'Error Checking for Updates',
                     'body': data['error'],
                     'params': '{closeButton: true, timeOut: 0, extendedTimeOut: 0}'
                     }
            Notification.add(notif)

        elif data['status'] == 'behind':
            if data['behind_count'] == 1:
                title = '1 Update Available'
            else:
                title = '{} Updates Available'.format(data['behind_count'])

            compare = '{}/compare/{}...{}'.format(core.GIT_URL, data['new_hash'], data['local_hash'])

            notif = {'type': 'update',
                     'title': title,
                     'body': 'Click to update now. <br/> Click <a href="'+compare+'" target="_blank"><u>here</u></a> to view changes.',
                     'params': {'closeButton': 'true',
                                'timeOut': 0,
                                'extendedTimeOut': 0,
                                'onclick': 'update_now'}
                     }

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

        taskscheduler.ScheduledTask(hr, min, interval, AutoUpdateInstall.install,
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
        update = ver.manager.execute_update()
        core.UPDATING = False

        if not update:
            logging.error('Update failed.')

        logging.info('Update successful, restarting.')
        cherrypy.engine.restart()
        return
