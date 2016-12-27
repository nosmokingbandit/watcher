import dominate
from cherrypy import expose
from dominate.tags import *
from header import Header
from head import Head
from footer import Footer

class AddMovie():
    @expose
    def index(self):
        doc = dominate.document(title='Watcher')

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href='static/css/add_movie.css')
            link(rel='stylesheet', href='static/css/movie_info_popup.css')
            script(type='text/javascript', src='static/js/add_movie/main.js')

        with doc:
            Header.insert_header(current="add_movie")
            with div(id='search_box'):
                input(id='search_input', type="text", placeholder="Search...", name="search_term")
                with button(id="search_button"):
                    i(cls='fa fa-search')
            Footer.insert_footer()
            div(id='thinker')

            with div(id="database_results"):
                ul(id='movie_list')

            div(id='overlay')

            div(id='info_pop_up')

        return doc.render()
