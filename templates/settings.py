import cherrypy
import core
import dominate
from cherrypy import expose
from core import config
from dominate.tags import *
from header import Header
from head import Head
from footer import Footer

def settings_page(page):
    ''' Decorator template for settings subpages
    :param page: Sub-page content to render, written with Dominate tags, but without a Dominate instance.

    Returns rendered html from Dominate.
    '''

    def page_template(self):
        config = core.CONFIG
        doc = dominate.document(title='Watcher')

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/settings.css')
            script(type='text/javascript', src=core.URL_BASE + '/static/js/settings/main.js?v=12.27')
            script(type='text/javascript', src=core.URL_BASE + '/static/js/settings/save_settings.js?v=12.27')

        with doc:
            Header.insert_header(current="settings")
            with div(id="content"):
                page(config)
            Footer.insert_footer()
        return doc.render()

    return page_template


class Settings():

    def __init__(self):
        return

    @expose
    def index(self):
        raise cherrypy.HTTPRedirect(core.URL_BASE + 'settings/server')

    @expose
    @settings_page
    def server(c):
        h1('Server')
        c_s = 'Server'
        with ul(id='server', cls='wide'):
            with li('Host: ', cls='bbord'):
                input(type='text', id='serverhost', value=c[c_s]['serverhost'], style='width: 17em')
                span('Typically localhost or 127.0.0.1.', cls='tip')
            with li('Port: ', cls='bbord'):
                input(type='number', id='serverport', value=c[c_s]['serverport'], style='width: 5em')
            with li('API Key: ', cls='bbord'):
                input(type='text', id='apikey', value=c[c_s]['apikey'], style='width: 20em')
                with span(cls='tip'):
                    i(id='generate_new_key', cls='fa fa-refresh')
                    span('Generate new key.')
            with li():
                i(id='authrequired', cls='fa fa-square-o checkbox', value=c[c_s]['authrequired'])
                span('Password-protect web-ui.')
                span('*Requires restart.', cls='tip')
            with li('Name: '):
                input(type='text', id='authuser', value=c[c_s]['authuser'], style='width: 20em')
            with li('Password: ', cls='bbord'):
                input(type='text', id='authpass', value=c[c_s]['authpass'], style='width: 20em')
            with li(cls='bbord'):
                i(id='launchbrowser', cls='fa fa-square-o checkbox', value=c[c_s]['launchbrowser'])
                span('Open browser on launch.')
            with li(cls='bbord'):
                i(id='checkupdates', cls='fa fa-square-o checkbox', value=c[c_s]['checkupdates'])
                span('Check for updates every ')
                input(type='number', min='8', id='checkupdatefrequency', value=c[c_s]['checkupdatefrequency'], style='width: 2.25em')
                span(' hours.')
                span('Checks at program start and every X hours afterward. *Requires restart.', cls='tip')
            with li(cls='bbord'):
                i(id='installupdates', cls='fa fa-square-o checkbox', value=c[c_s]['installupdates'])
                span('Automatically install updates at ')
                input(type='number', min='0', max='23', id='installupdatehr', value=c[c_s]['installupdatehr'], style='width: 2.25em')
                span(':')
                input(type='number', min='0', max='59', id='installupdatemin', value=c[c_s]['installupdatemin'], style='width: 2.25em')
                span('24hr time. *Requires restart.', cls='tip')
            with li(cls='bbord'):
                with span(id='update_check'):
                    i(cls='fa fa-arrow-circle-up')
                    span('Check for updates now.')
            with li(cls='bbord'):
                span('Keep ')
                input(type='number', id='keeplog', value=c[c_s]['keeplog'], style='width: 3em')
                span(' days of logs.')
            with li():
                with span(id='restart'):
                    i(cls='fa fa-refresh')
                    span('Restart')
                with span(id='shutdown'):
                    i(cls='fa fa-power-off')
                    span('Shutdown')
                with span('Current version hash: ', cls='tip'):
                    if core.CURRENT_HASH is not None:
                        a(core.CURRENT_HASH[0:7], href='{}/commits'.format(core.GIT_URL))

        with span(id='save', cat='server'):
            i(cls='fa fa-save')
            span('Save Settings')

    @expose
    @settings_page
    def search(c):
        h1('Search', id='searchform')
        # set the config section at each new section. Just makes everything a little shorter and easier to write.
        c_s = 'Search'
        with ul(id='search', cls='wide'):
            with li(cls='bbord'):
                i(id='searchafteradd', cls='fa fa-square-o checkbox', value=c[c_s]['searchafteradd'])
                span('Search immediately after adding movie.')
                span('Skips wait until next scheduled search.', cls='tip')
            with li(cls='bbord'):
                i(id='autograb', cls='fa fa-square-o checkbox', value=c[c_s]['autograb'])
                span('Automatically grab best result.')
                span('Will still wait X days if set.', cls='tip')
            with li(cls='bbord'):
                span('Search time:')
                input(type='number', min='0', max='23', id='searchtimehr', style='width: 2.5em', value=c[c_s]['searchtimehr'])
                span(':')
                input(type='number', min='0', max='59', id='searchtimemin', style='width: 2.5em', value=c[c_s]['searchtimemin'])
                span('What time of day to begin searches (24h time). Requires Restart.', cls='tip')
            with li(cls='bbord'):
                span('Search every ')
                input(type='number', min='1', id='searchfrequency', style='width: 2.5em', value=c[c_s]['searchfrequency'])
                span('hours.')
                span('Once releases are available according to predb.me. Requires Restart.', cls='tip')
            with li(cls='bbord'):
                span('Wait ')
                input(type='number', min='0', max='14', id='waitdays', style='width: 2.0em', value=c[c_s]['waitdays'])
                span(' days for best release.')
                span('After movie is found, wait to snatch in case better match is found.', cls='tip')
            with li(cls='bbord'):
                i(id='keepsearching', cls='fa fa-square-o checkbox', value=c[c_s]['keepsearching'])
                span('Continue searching for ')
                input(type='number', min='0', id='keepsearchingdays', style='width: 2.5em', value=c[c_s]['keepsearchingdays'])
                span(' days for best release.')
            with li():
                span('Retention: ')
                input(type='number', min='0', id='retention', value=c[c_s]['retention'])
                span(' days.')
                span('Use 0 for no limit.', cls='tip')

        with span(id='save', cat='search'):
            i(cls='fa fa-save')
            span('Save Settings')

    @expose
    @settings_page
    def quality(c):
        span('Quality and Filters may be set separately for each movie, this is the '\
          'default setting that will be used to \'Quick-Add\' movies.')
        br()
        h1('Quality')
        c_s = 'Quality'
        resolutions = ['4K', '1080P', '720P', 'SD']
        with ul(id='quality', cls='wide'):
            # Resolution Block
            with ul(id='resolution', cls='sortable'):
                span('Resolutions', cls='sub_cat not_sortable')

                for res in resolutions:
                    prior = '{}priority'.format(res)
                    with li(cls='rbord', id=prior, sort=c[c_s][res][1]):
                        i(cls='fa fa-bars')
                        i(id=res, cls='fa fa-square-o checkbox', value=c[c_s][res][0])
                        span(res)

            # Size restriction block
            with ul(id='resolution_size'):
                li('Size Restrictions (MB)', cls='sub_cat')

                for res in resolutions:
                    min = '{}min'.format(res)
                    max = '{}max'.format(res)
                    with li():
                        span(res)
                        input(type='number', id=min, value=c[c_s][res][2], min='0', style='width: 7.5em')
                        input(type='number', id=max, value=c[c_s][res][3], min='0', style='width: 7.5em')

        div(','.join(resolutions), cls='hidden_data')

        h1('Filters', id='filter_form')
        # set the config section at each new section. Just makes everything a little shorter and easier to write.
        c_s = 'Filters'
        with ul(id='filters', cls='wide'):
            with li(cls='bbord'):
                span('Required words:')
                input(type='text', id='requiredwords', value=c[c_s]['requiredwords'], style='width: 16em')
                span('Releases must contain these words.', cls='tip')
            with li(cls='bbord'):
                span('Preferred words:')
                input(type='text', id='preferredwords', value=c[c_s]['preferredwords'], style='width: 16em')
                span('Releases with these words score higher.', cls='tip')
            with li():
                span('Ignored words:')
                input(type='text', id='ignoredwords', value=c[c_s]['ignoredwords'], style='width: 16em')
                span('Releases with these words are ignored.', cls='tip')

        with span(id='save', cat='quality'):
            i(cls='fa fa-save')
            span('Save Settings')

    @expose
    @settings_page
    def providers(c):
        h1('Indexers')
        c_s = 'Indexers'
        with ul(id='indexers', cls='wide'):
            with li():
                with ul(id='newznab_list'):
                    with li(cls='sub_cat'):
                        span('NewzNab Indexers')

                    for n in c[c_s]:
                        with li(cls='newznab_indexer'):
                            i(cls='newznab_check fa fa-square-o checkbox', value=c[c_s][n][2])
                            input(type='text', cls='newznab_url', value=c[c_s][n][0], placeholder=" http://www.indexer-url.com/")
                            input(type='text', cls='newznab_api', value=c[c_s][n][1], placeholder=" Api Key")
                    with li(id='add_newznab_row'):
                        i(cls='fa fa-plus-square', id='add_row')

        with span(id='save', cat='providers'):
            i(cls='fa fa-save')
            span('Save Settings')

    @expose
    @settings_page
    def downloader(c):
        h1('Downloader')
        with ul(id='downloader'):
            c_s = 'Sabnzbd'
            with li(cls='bbord'):
                i(id='sabenabled', cls='fa fa-circle-o radio', tog='sabnzbd', value=c[c_s]['sabenabled'])
                span('Sabnzbd', cls='sub_cat')
            # I'm not 100% sure it is valid to do a ul>ul, but it only work this way so deal with it.
            with ul(id='sabnzbd'):
                with li('Host & Port: ', cls='bbord'):
                    input(type='text', id='sabhost', value=c[c_s]['sabhost'], style='width: 25%')
                    span(' : ')
                    input(type='text', id='sabport', value=c[c_s]['sabport'], style='width: 25%')
                with li('Api Key: ', cls='bbord'):
                    input(type='text', id='sabapi', value=c[c_s]['sabapi'], style='width: 50%')
                    span('Please use full api key.', cls='tip')
                with li('Category: ', cls='bbord'):
                    input(type='text', id='sabcategory', value=c[c_s]['sabcategory'], style='width: 50%')
                    span('i.e. \'movies\', \'watcher\'. ', cls='tip')
                with li('Priority: ', cls='bbord'):
                    with select(id='sabpriority', value=c[c_s]['sabpriority'], style='width: 50%'):
                        pl = ['Paused', 'Low', 'Normal', 'High', 'Forced']
                        for o in pl:
                            if o == c[c_s]['sabpriority']:
                                option(o, value=o, selected="selected")
                            else:
                                option(o, value=o)

                with li():
                    with span(cls='test_connection', mode='sabnzbd'):
                        i(cls='fa fa-plug')
                        span('Test Connection')
            c_s = 'NzbGet'
            with li():
                i(id='nzbgenabled', cls='fa fa-circle-o radio', tog='nzbget', value=c[c_s]['nzbgenabled'])
                span('NZBGet', cls='sub_cat')
            with ul(id='nzbget'):
                with li('Host & Port: ', cls='bbord'):
                    input(type='text', id='nzbghost', value=c[c_s]['nzbghost'], style='width: 25%')
                    span(' : ')
                    input(type='text', id='nzbgport', value=c[c_s]['nzbgport'], style='width: 25%')
                with li('User Name: ', cls='bbord'):
                    input(type='text', id='nzbguser', value=c[c_s]['nzbguser'], style='width: 50%')
                    span('Default: nzbget.', cls='tip')
                with li('Password: ', cls='bbord'):
                    input(type='text', id='nzbgpass', value=c[c_s]['nzbgpass'], style='width: 50%')
                    span('Default: tegbzn6789.', cls='tip')
                with li('Category: ', cls='bbord'):
                    input(type='text', id='nzbgcategory', value=c[c_s]['nzbgcategory'], style='width: 50%')
                    span('i.e. \'movies\', \'watcher\'. ', cls='tip')
                with li('Priority: ', cls='bbord'):
                    with select(id='nzbgpriority', style='width: 50%'):
                        pl = ['Very Low', 'Low', 'Normal', 'High', 'Forced']
                        for o in pl:
                            if o == c[c_s]['nzbgpriority']:
                                option(o, value=o, selected="selected")
                            else:
                                option(o, value=o)
                with li(cls='bbord'):
                    i(id='nzbgaddpaused', cls='fa fa-square-o checkbox', value=c[c_s]['nzbgaddpaused'])
                    span('Add Paused')

                with li():
                    with span(cls='test_connection', mode='nzbget'):
                        i(cls='fa fa-plug')
                        span('Test Connection')

        with span(id='save', cat='downloader'):
            i(cls='fa fa-save')
            span('Save Settings')

    @expose
    @settings_page
    def postprocessing(c):
        h1('Post-Processing')
        c_s = 'Postprocessing'
        with ul(id='postprocessing'):
            with li(cls='bbord'):
                i(id='cleanupfailed', cls='fa fa-square-o checkbox', value=c[c_s]['cleanupfailed'])
                span('Delete leftover files after a failed download.')
            with li(cls='bbord'):
                i(id='renamerenabled', cls='fa fa-square-o checkbox', value=c[c_s]['renamerenabled'])
                span('Enable Renamer')
            with ul(id='renamer'):
                with li():
                    input(id='renamerstring', type='text', style='width: 80%', value=c[c_s]['renamerstring'])
                    br()
                    span('Example: ')
                    br()
                    span('{title} {year} - {videocodec} = How to Train Your Dragon 2010 - x264.mkv',  cls='taglist')

            with li(cls='bbord'):
                i(id='moverenabled', cls='fa fa-square-o checkbox', value=c[c_s]['moverenabled'])
                span('Enable Mover')
            with ul(id='mover'):
                with li():
                    span('Move movie file to: ')
                    input(type='text', style='width: 28em', id='moverpath', value=c[c_s]['moverpath'])
                    span('Use absolute path.', cls='tip')
                    br()
                    span('Example: ')
                    br()
                    span('/home/user/movies/{title} {year} = /home/user/movies/Black Swan 2010/',  cls='taglist')
                    br()
                    i(id='cleanupenabled', cls='fa fa-square-o checkbox', value=c[c_s]['cleanupenabled'])
                    span('Clean up after move.')
            with li('Available tags:'):
                span('{title} {year} {resolution} {rated} {imdbid} {videocodec} {audiocodec} {releasegroup} {source}', cls='taglist')

        with span(id='save', cat='postprocessing'):
            i(cls='fa fa-save')
            span('Save Settings')

    @expose
    @settings_page
    def about(c):
        with div(cls='about'):
            h1('About Watcher')

            h2('Source')
            with p():
                span('Watcher is hosted and maintained on GitHub. You may view the repository at ')
                a('https://github.com/', href='https://github.com/nosmokingbandit/watcher')

            h2('License')
            with p():
                span('''
                    Watcher is open-source and licensed under the Apache 2.0 license. The essence of the
                    Apache 2.0 license is that any user can, for any reason, modify, distribute, or
                    repackage the licesed software with the condition that this license is included with,
                    and remains applicable to, any derivative works. You may not use the Watcher logo
                    or design elements without express approval by the owner. You may not hold the
                    developers of Watcher liable for any damages incurred from use.
                    '''
                     )
            with p():
                span('You may view the full, binding license at ')
                a('http://www.apache.org/', href='http://www.apache.org/licenses/LICENSE-2.0.html')
                span(' or in license.txt included in the root folder of Watcher.')
            h2('Attribution')
            with p():
                span('''
                    Watcher is only possible because of the amazing open-source works that are
                    included in this package. The Watcher license does not apply to these
                    properties. Please check each package's license requirements when using them
                    in your own work.
                    '''
                     )
            with ul(id='libraries'):
                with li():
                    a('CherryPy', href='http://cherrypy.org/')
                with li():
                    a('SQLAlchemy', href='http://www.sqlalchemy.org/')
                with li():
                    a('Six', href='https://pypi.python.org/pypi/six')
                with li():
                    a('FuzzWuzzy', href='https://pypi.python.org/pypi/fuzzywuzzy')
                with li():
                    a('Font-Awesome', href='http://fontawesome.io/')
                with li():
                    a('JQuery', href='https://jquery.com/')
                with li():
                    a('Parse Torrent Name', href='https://pypi.python.org/pypi/parse-torrent-name')
