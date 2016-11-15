import dominate
from dominate.tags import *
import json
import sys
from core.movieinfo import Omdb, Trailer

class MovieInfoPopup():

    def html(self, imdbid):
        omdb = Omdb()
        trailer = Trailer()

        data = omdb.movie_info(imdbid)
        data_json = json.dumps(data)

        title_date = data['title'] + ' '+  data['year']
        imdbid = data['imdbid']
        youtube_id = trailer.get_trailer(title_date)
        trailer_embed = "https://www.youtube.com/embed/{}?&showinfo=0".format(youtube_id)
        if data['poster'] == 'N/A':
            data['poster'] = 'images/missing_poster.jpg'

        doc = dominate.document()

        with doc.head:
            base(href="/static/")
            script(src='js/add_movie/movie_info_popup.js')

        with doc:
            with div(id='container'):
                with div(id='title'):
                    with p():
                        span(title_date, id='title')
                        button('ADD', id='add', imdbid=imdbid)
                with div(id='media'):
                    img(id='poster', src=data['poster'])
                    iframe(id='trailer', width="640", height="360", src=trailer_embed, frameborder="0")
                with div(id='plot'):
                    p(data['plot'])
                with div(id='additional_info'):
                    with a(href=data['tomatourl'], target='_blank'):
                        p('Rotten Tomatoes Rating: {}'.format(data['tomatorating']) )
                    p('Theatrical Release Date: {}'.format(data['released']))
                    p('DVD Release Date: {}'.format(data['dvd']))
                div(data_json, id='hidden_data')
        return doc.render()


