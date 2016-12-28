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

        base = {'icon': '',
                'title': '',
                'title_link': '',
                'text': '',
                'button': ''
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

    @staticmethod
    def remove(index):
        ''' Removes notification from core.notification
        :param index: int index of notification to remove

        Replaces list item with None as to not affect other indexes.

        When adding new notifs through core.notification, any None values
            will be overwritten before appending to the end of the list.
        Removes all trailing 'None' entries in list.

        This ensures the list will always be as small as possible without
            changing existing indexes.

        Does not return
        '''

        core.NOTIFICATIONS[int(index)] = None

        while len(core.NOTIFICATIONS) > 0 and core.NOTIFICATIONS[-1] is None:
            core.NOTIFICATIONS.pop()

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
