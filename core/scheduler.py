import cherrypy
from datetime import datetime
from datetime import timedelta
from threading import Timer
import core
from core import config, searcher
from cherrypy.process import plugins
from log import log

import logging
logging = logging.getLogger(__name__)

class SchedulerPlugin(plugins.SimplePlugin):

    def __init__(self, bus):
        plugins.SimplePlugin.__init__(self, bus)

    def start(self):
        self.bus.log('Starting up Scheduler plugin.')
        logging.info('Starting up Scheduler plugin.')

        self.auto_search = ScheduledTasks.AutoSearch()
        self.auto_search.start()

    def stop(self):
        self.bus.log('Stopping Scheduler plugin, waiting for tasks to complete.')
        logging.info('Stopping Scheduler plugin, waiting for tasks to complete.')

        self.auto_search.stop()

class ScheduledTasks(object):

    def __init__(self):
        return

    class Manager(object):
        def start(self):
            self.task.timer.start()

        def stop(self):
            self.task.timer.cancel()

        def reload(self):
            try:
                self.task.timer.cancel()
                self.__init__()
                self.task.timer.start()
                return True
            except Exception as e:
                return e

    class AutoSearch(Manager):

        def __init__(self):
            self.searcher = searcher.Searcher()
            conf = config.Config()
            hr = int(conf['Search']['searchtimehr'])
            min = int(conf['Search']['searchtimemin'])
            interval = int(conf['Search']['searchfrequency'])
            self.task = Task(hr, min, interval, self.searcher.auto_search_and_grab)

class Task(object):
    def __init__(self, hour, minute, interval, func):
        self.interval = interval * 3600
        self.func = func

        now = datetime.today().replace(second=0, microsecond=0)
        next = now.replace(hour = hour, minute = minute)

        while next < now:
            next += timedelta(seconds=self.interval)

        self.delay = (next - now).seconds
        core.NEXT_SEARCH = now + timedelta(0, self.delay)
        self.timer = Timer(self.delay, self.task)

    def task(self):
        self.func()
        now = datetime.today().replace(second=0, microsecond=0)
        core.NEXT_SEARCH = now + timedelta(0, self.interval)
        self.timer = Timer(self.interval, self.task)
        self.timer.start()

'''
Global commands
cherrypy.engine.scheduler.{taskname}.stop()
                                    .restart()
                                    .start()
Restart entire engine:
cherrypy.engine.graceful()


To add new task:

Create new class, inherit Manager
In __init__
    gather time of day to start, interval, and function to fire. Pass to scheduler like this:
    self.named_task = Task(hr, min, interval, self.searcher.auto_search)

In class ScheduledTasks, add to start, stop, and restart. I'll eventually make a list of tasks and have start/stop/resart iterate over, but that is a job for tomorrow.

'''
