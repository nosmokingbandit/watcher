from dominate.tags import *
import core


class Head(object):

    @staticmethod
    def insert():
        meta(name='robots', content='noindex, nofollow')
        meta(name='url_base', content=core.URL_BASE)

        link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/style.css'.format(core.THEME))
        link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')
        link(rel='stylesheet', href=core.URL_BASE + '/static/font-awesome/css/font-awesome.css')
        link(rel='stylesheet', href=core.URL_BASE + '/static/js/sweetalert-master/dist/sweetalert.css')
        script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js')
        script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.0/jquery-ui.min.js')
        script(type='text/javascript', src=core.URL_BASE + '/static/js/sweetalert-master/dist/sweetalert-dev.js')
        script(type='text/javascript', src=core.URL_BASE + '/static/js/notification/main.js?v=12.27')
