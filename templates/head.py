import core
import json
from dominate.tags import *


class Head(object):
    ''' Inserts shared header content.

    Includes shares javascrpt, css, metadata, etc.
    '''

    @staticmethod
    def insert():
        meta(name='robots', content='noindex, nofollow')
        meta(name='url_base', content=core.URL_BASE)
        meta(name='notifications', content=json.dumps([i for i in core.NOTIFICATIONS if i is not None]))

        link(rel='stylesheet', href=core.URL_BASE + '/static/css/style.css')
        link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/style.css'.format(core.CONFIG['Server']['theme']))
        link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')
        link(rel='stylesheet', href=core.URL_BASE + '/static/font-awesome/css/font-awesome.css')
        link(rel='stylesheet', href=core.URL_BASE + '/static/js/sweetalert-master/dist/sweetalert.css')
        link(rel='stylesheet', href=core.URL_BASE + '/static/js/toastr/toastr.css')
        script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js')
        script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.0/jquery-ui.min.js')
        script(type='text/javascript', src=core.URL_BASE + '/static/js/sweetalert-master/dist/sweetalert-dev.js')
        script(type='text/javascript', src=core.URL_BASE + '/static/js/toastr/toastr.min.js')
        script(type='text/javascript', src=core.URL_BASE + '/static/js/notification/main.js?v=01.05')
        script("toastr.options.positionClass = 'toast-bottom-left'; toastr['update'] = toastr['info'];toastr.options.preventDuplicates = true; toastr.options.closeButton = true", type='text/javascript')

# pylama:ignore=W0401
