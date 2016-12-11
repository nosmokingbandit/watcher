from dominate.tags import *

class Header():
    @staticmethod
    def insert_header(current):
        menu_items = ['Settings', 'Add Movie', 'Status']

        with div(id='header'):
            with div(id='header_container'):
                img(src='images/logo.png', alt='')
                with ul(id='nav'):
                    for i in menu_items:
                        i_lower = i.lower().replace(' ', '_')
                        with a(href='/{}'.format(i_lower)):
                            if i_lower == current:
                                li(i, cls=(i_lower + ' current'))
                            else:
                                li(i, cls=i_lower)
