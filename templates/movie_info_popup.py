import json

import core
from core.movieinfo import Omdb, Trailer
from dominate.tags import *


class MovieInfoPopup():

    def __init__(self):
        return

    def html(self, imdbid):

        omdb = Omdb()
        trailer = Trailer()

        data = omdb.movie_info(imdbid)
        if not data:
            return self.no_data()

        data_json = json.dumps(data)

        title_date = data['title'] + ' ' + data['year']
        imdbid = data['imdbid']
        youtube_id = trailer.get_trailer(title_date)

        if youtube_id:
            trailer_embed = "https://www.youtube.com/embed/{}?&showinfo=0".format(youtube_id)
        else:
            trailer_embed = ''
        if data['poster'] == 'N/A':
            data['poster'] = core.URL_BASE + '/static/images/missing_poster.jpg'

        container = div(id='container')
        with container:
            script(type='text/javascript', src=core.URL_BASE + '/static/js/add_movie/movie_info_popup.js?v=01.03')
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
                    resolutions = ['4K', '1080P', '720P', 'SD']
                    with ul(id='quality', cls='wide'):
                        # Resolution Block
                        with ul(id='resolution', cls='sortable'):
                            span(u'Resolutions', cls='sub_cat not_sortable')

                            for res in resolutions:
                                prior = '{}priority'.format(res)
                                with li(cls='rbord', id=prior, sort=core.CONFIG['Quality'][res][1]):
                                    i(cls='fa fa-bars')
                                    i(id=res, cls='fa fa-square-o checkbox', value=core.CONFIG['Quality'][res][0])
                                    span(res)

                        # Size restriction block
                        with ul(id='resolution_size'):
                            with li(u'Size Restrictions (MB)', cls='sub_cat'):

                                for res in resolutions:
                                    min = '{}min'.format(res)
                                    max = '{}max'.format(res)
                                    with li():
                                        span(res)
                                        input(type='number', id=min, value=core.CONFIG['Quality'][res][2], min='0', style='width: 7.5em')
                                        input(type='number', id=max, value=core.CONFIG['Quality'][res][3], min='0', style='width: 7.5em')

                        with ul(id='filters', cls='wide'):
                            with li(cls='bbord'):
                                span(u'Required words:')
                                input(type='text', id='requiredwords', value=core.CONFIG['Filters']['requiredwords'])
                            with li(cls='bbord'):
                                span(u'Preferred words:')
                                input(type='text', id='preferredwords', value=core.CONFIG['Filters']['preferredwords'])
                            with li():
                                span(u'Ignored words:')
                                input(type='text', id='ignoredwords', value=core.CONFIG['Filters']['ignoredwords'])

            with div(id='plot'):
                p(data['plot'])
            with div(id='additional_info'):
                with a(href=data['tomatourl'], target='_blank'):
                    p(u'Rotten Tomatoes Rating: {}'.format(data['tomatorating']))
                p(u'Theatrical Release Date: {}'.format(data['released']))
                p(u'DVD Release Date: {}'.format(data['dvd']))
            div(data_json, id='hidden_data')

        return unicode(container)

    def no_data(self):
        message = "<div id='container'><span>Unable to retrive movie information. Try again in a few minutes or check logs for more information.</span></div>"
        return message

# pylama:ignore=W0401
