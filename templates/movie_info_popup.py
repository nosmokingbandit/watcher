import dominate
from dominate.tags import *
import json
import sys
from core.movieinfo import Omdb, Trailer
from core import config

class MovieInfoPopup():

    def __init__(self):
        self.config = config.Config()
        self.c = self.config.sections() ## can this be done better?
        # converts comma delimited values into lists
        for section in self.c:
            if section != 'Filters':
                for key in self.c[section]:
                    value = self.c[section][key]
                    if ',' in value:
                        self.c[section][key] = value.split(',')
            elif section == 'Filters':
                for key in self.c[section]:
                    value = self.c[section][key]
                    if ',' in value:
                        self.c[section][key] = value.replace(',', ', ')

    def html(self, imdbid):

        omdb = Omdb()
        trailer = Trailer()

        data = omdb.movie_info(imdbid)
        data_json = json.dumps(data)

        title_date = data['title'] + ' '+  data['year']
        imdbid = data['imdbid']
        youtube_id = trailer.get_trailer(title_date)
        if youtube_id:
            trailer_embed = "https://www.youtube.com/embed/{}?&showinfo=0".format(youtube_id)
        else:
            trailer_embed = ''
        if data['poster'] == 'N/A':
            data['poster'] = 'images/missing_poster.jpg'

        doc = dominate.document()

        with doc.head:
            base(href="/static/")

            script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.0/jquery-ui.min.js')

            script(src='js/add_movie/movie_info_popup.js')

        with doc:
            with div(id='container'):
                with div(id='title'):
                    with p():
                        span(title_date, id='title')
                        i(cls='fa fa-plus', id='button_add')
                        i(cls='fa fa-floppy-o', id='button_submit', imdbid=imdbid)
                with div(id='media'):
                    img(id='poster', src=data['poster'])
                    with div(id='trailer_container'):
                        iframe(id='trailer', width="640", height="360", src=trailer_embed, frameborder="0")

                        # Panel that swaps in with quality adjustments
                        resolutions = ['4K','1080P','720P','SD']
                        with ul(id='quality', cls='wide'):
                            # Resolution Block
                            with ul(id='resolution', cls='sortable'):
                                span('Resolutions', cls='sub_cat not_sortable')

                                for res in resolutions:
                                    prior = '{}priority'.format(res)
                                    with li(cls='rbord', id=prior, sort=self.c['Quality'][res][1]):
                                        i(cls='fa fa-bars')
                                        i(id=res, cls='fa fa-square-o checkbox', value=self.c['Quality'][res][0])
                                        span(res)

                            # Size restriction block
                            with ul(id='resolution_size'):
                                with li('Size Restrictions (MB)', cls='sub_cat'):

                                    for res in resolutions:
                                        min = '{}min'.format(res)
                                        max = '{}max'.format(res)
                                        with li():
                                            span(res)
                                            input(type='number', id=min, value=self.c['Quality'][res][2], min='0', style='width: 7.5em')
                                            input(type='number', id=max, value=self.c['Quality'][res][3], min='0', style='width: 7.5em')

                            with ul(id='filters', cls='wide'):
                                with li(cls='bbord'):
                                    span('Required words:')
                                    input(type='text', id='requiredwords', value=self.c['Filters']['requiredwords'], style='width: 16em')
                                with li(cls='bbord'):
                                    span('Preferred words:')
                                    input(type='text', id='preferredwords', value=self.c['Filters']['preferredwords'], style='width: 16em')
                                with li():
                                    span('Ignored words:')
                                    input(type='text', id='ignoredwords', value=self.c['Filters']['ignoredwords'], style='width: 16em')

                with div(id='plot'):
                    p(data['plot'])
                with div(id='additional_info'):
                    with a(href=data['tomatourl'], target='_blank'):
                        p('Rotten Tomatoes Rating: {}'.format(data['tomatorating']) )
                    p('Theatrical Release Date: {}'.format(data['released']))
                    p('DVD Release Date: {}'.format(data['dvd']))
                div(data_json, id='hidden_data')

        return doc.render()


