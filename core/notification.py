import core
import logging

logging = logging.getLogger(__name__)

class Notification(object):

    def __init__(self):
        return

    @staticmethod
    def add(data):
        ''' Adds notification to core.NOTIFICATIONS
        :param data: dict of notification information

        Merges supplied 'data' with 'base' dict t ensure no fields are missing
        Appends 'base' to core.NOTIFICATIONS

        Does not return
        '''

        base = {'icon': None,
                'title': None,
                'title_link': None,
                'text': None,
                'button': None
                }

        base.update(data)

        logging.info('Creating notification:')
        logging.info(base)

        # if there is a None in the list, overwrite it.
        for i, v in enumerate(core.NOTIFICATIONS):
            if v is None:
                core.NOTIFICATIONS[i] = base
                return
        # if not just append
        core.NOTIFICATIONS.append(base)
        return
