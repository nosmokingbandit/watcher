from dominate.tags import *
import core
from core import config

class Head(object):

    def __init__(self):
        return

    @staticmethod
    def insert():
        meta(name='robots', content='noindex, nofollow')
        meta(name='url_base', content=core.URL_BASE)
        theme=str(core.CONFIG['Server']['csstheme'])
        
        link(rel='stylesheet', href=core.URL_BASE + '/static/css/'+theme+'/style.css')
        link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')
        link(rel='stylesheet', href=core.URL_BASE + '/static/font-awesome/css/font-awesome.css')
        link(rel='stylesheet', href=core.URL_BASE + '/static/css/'+theme+'/sweetalert.css')
        script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js')
        script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.0/jquery-ui.min.js')
        script(type='text/javascript', src=core.URL_BASE + '/static/js/sweetalert-master/dist/sweetalert-dev.js')
        script(type='text/javascript', src=core.URL_BASE + '/static/js/notification/main.js?v=12.27')
