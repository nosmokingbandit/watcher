from datetime import datetime
from datetime import timedelta
from datetime import date
import os
from core import config
import logging
import logging.handlers

class log(object):

    @staticmethod
    def start():
        conf = config.Config()
        path = 'logs/log.txt'
        backup_days = int(conf['Server']['keeplog'])
        logging_level = logging.INFO

        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        handler = logging.handlers.TimedRotatingFileHandler(path, when="D", interval=1, backupCount=backup_days)
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging_level)

        return
