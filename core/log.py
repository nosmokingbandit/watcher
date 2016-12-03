from datetime import datetime
from datetime import timedelta
from datetime import date
import os
import core
import logging
import logging.handlers

class log(object):

    @staticmethod
    def start():
        if not os.path.exists('logs'):
            os.makedirs('logs')

        path = 'logs/log.txt'
        backup_days = int(core.CONFIG['Server']['keeplog'])
        logging_level = logging.INFO

        formatter = logging.Formatter('%(levelname)s %(asctime)s %(name)s.%(funcName)s: %(message)s')
        handler = logging.handlers.TimedRotatingFileHandler(path, when="D", interval=1, backupCount=backup_days)
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging_level)

        return
