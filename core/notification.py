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

        # if it already exists, ignore it
        if base in core.NOTIFICATIONS:
            return

        # if there is a None in the list, overwrite it.
        for i, v in enumerate(core.NOTIFICATIONS):
            if v is None:
                core.NOTIFICATIONS[i] = base
                return
        # if not just append
        core.NOTIFICATIONS.append(base)
        return


'''
NOTIFICATION dict:

'icon': None,       str font awesome icon 'fa-star'
'title': None,      str large title text 'Something Happened!'
'title_link': None, str url for title to link to.
'text': None,       str main body text explaining title if necessary
'button': None      tuple ('Name', '/url/link' , 'fa-refresh')

All Ajax  requests should be specified in static/notifications/main.js

'''
