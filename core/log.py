from datetime import datetime
from datetime import timedelta
from datetime import date
import os
import core
import logging
import logging.handlers

class log(object):

    @staticmethod
    def start(path):
        if not os.path.exists(path):
            os.makedirs(path)

        logfile = os.path.join(path, 'log.txt')
        backup_days = int(core.CONFIG['Server']['keeplog'])
        logging_level = logging.INFO

        formatter = logging.Formatter('%(levelname)s %(asctime)s %(name)s.%(funcName)s: %(message)s')
        handler = logging.handlers.TimedRotatingFileHandler(logfile, when="D", interval=1, backupCount=backup_days)
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging_level)

        return
