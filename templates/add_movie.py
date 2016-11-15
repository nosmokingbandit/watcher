from cherrypy import expose
import dominate
from dominate.tags import *
from header import Header

class AddMovie():
    @expose
    def index(self):
        doc = dominate.document(title='Watcher')

        with doc.head:
            base(href="/static/")

            link(rel='stylesheet', href='css/style.css')
            link(rel='stylesheet', href='css/add_movie.css')
            link(rel='stylesheet', href='css/movie_info_popup.css')
            link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')

            script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js')
            script(src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.0/jquery-ui.min.js")

            script(type='text/javascript', src='js/add_movie/main.js')


        with doc:
            Header.insert_header(current="add_movie")
            with div(id='search_box'):
                input(id='search_input',type="text", placeholder="Search...", name="search_term")
                with button(id="search_button"):
                    i('search', cls='material-icons')

            div(id='thinker')

            with div(id="database_results"):
                ul(id='movie_list')

            div(id='overlay')

            div(id='info_pop_up')

        return doc.render()
