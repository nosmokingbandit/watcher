from dominate.tags import *

class Head(object):

    def __init__(self):
        return

    @staticmethod
    def insert():
        base(href="../")

        link(rel='stylesheet', href='static/css/style.css')
        link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')
        link(rel='stylesheet', href='static/font-awesome/css/font-awesome.css')
        link(rel='stylesheet', href='static/js/sweetalert-master/dist/sweetalert.css')
        script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js')
        script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.0/jquery-ui.min.js')
        script(type='text/javascript', src='static/js/sweetalert-master/dist/sweetalert-dev.js')
        script(type='text/javascript', src='static/js/notification/main.js')
