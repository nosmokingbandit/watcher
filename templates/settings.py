import os

import cherrypy
import core
import dominate

from cherrypy import expose
from dominate.tags import *
from header import Header
from head import Head


def settings_page(page):
    ''' Decorator template for settings subpages
    :param page: Sub-page content to render, written with Dominate tags, but without a Dominate instance.

    Returns rendered html from Dominate.
    '''

    def page_template(self):
        config = core.CONFIG
        doc = dominate.document(title='Watcher')

        with doc.head:
            meta(name='git_url', content=core.GIT_URL)
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/settings.css')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/settings.css'.format(core.THEME))
            script(type='text/javascript', src=core.URL_BASE + '/static/js/settings/main.js?v=01.05')
            script(type='text/javascript', src=core.URL_BASE + '/static/js/settings/save_settings.js?v=01.08')

        with doc:
            Header.insert_header(current="settings")
            with div(id="content"):
                page(self, config)

        return doc.render()

    return page_template


class Settings():

    @expose
    def default(self):
        raise cherrypy.InternalRedirect(core.URL_BASE + 'settings/server')

    @expose
    @settings_page
    def server(self, c):
        h1(u'Server')
        c_s = 'Server'
        with ul(id='server', cls='wide'):
            with li(u'Host: ', cls='bbord'):
                input(type='text', id='serverhost', value=c[c_s]['serverhost'], style='width: 17em')
                span(u'Typically localhost or 127.0.0.1.', cls='tip')
            with li(u'Port: ', cls='bbord'):
                input(type='number', id='serverport', value=c[c_s]['serverport'], style='width: 5em')
            with li(u'API Key: ', cls='bbord'):
                input(type='text', id='apikey', value=c[c_s]['apikey'], style='width: 20em')
                with span(cls='tip'):
                    i(id='generate_new_key', cls='fa fa-refresh')
                    span(u'Generate new key.')
            with li(u'Theme:', cls='bbord'):
                with select(id='theme', value=c[c_s]['theme']) as theme_select:
                    tl = self.get_themes()
                    for opt in tl:
                        if opt == 'Default':
                            item = option(opt, value='')
                        else:
                            item = option(opt, value=opt)
                        if item['value'] == c[c_s]['theme']:
                            item['selected'] = 'selected'
                            theme_select['value'] = opt
                span(u'*Requires restart.', cls='tip')

            with li():
                i(id='authrequired', cls='fa fa-square-o checkbox', value=c[c_s]['authrequired'])
                span(u'Password-protect web-ui.')
                span(u'*Requires restart.', cls='tip')
            with li(u'Name: '):
                input(type='text', id='authuser', value=c[c_s]['authuser'], style='width: 20em')
            with li(u'Password: ', cls='bbord'):
                input(type='text', id='authpass', value=c[c_s]['authpass'], style='width: 20em')
            with li(cls='bbord'):
                i(id='launchbrowser', cls='fa fa-square-o checkbox', value=c[c_s]['launchbrowser'])
                span(u'Open browser on launch.')
            with li(cls='bbord'):
                i(id='checkupdates', cls='fa fa-square-o checkbox', value=c[c_s]['checkupdates'])
                span(u'Check for updates every ')
                input(type='number', min='8', id='checkupdatefrequency', value=c[c_s]['checkupdatefrequency'], style='width: 2.25em')
                span(u' hours.')
                span(u'Checks at program start and every X hours afterward. *Requires restart.', cls='tip')
            with li(cls='bbord'):
                i(id='installupdates', cls='fa fa-square-o checkbox', value=c[c_s]['installupdates'])
                span(u'Automatically install updates at ')
                input(type='number', min='0', max='23', id='installupdatehr', value=c[c_s]['installupdatehr'], style='width: 2.25em')
                span(u':')
                input(type='number', min='0', max='59', id='installupdatemin', value=c[c_s]['installupdatemin'], style='width: 2.25em')
                span(u'24hr time. *Requires restart.', cls='tip')
            with li(cls='hidden'):
                input(type='text', id='gitbranch', value=c[c_s]['gitbranch'])
            with li(cls='bbord'):
                with span(id='update_check'):
                    i(cls='fa fa-arrow-circle-up')
                    span(u'Check for updates now.')
            with li(cls='bbord'):
                span(u'Keep ')
                input(type='number', id='keeplog', value=c[c_s]['keeplog'], style='width: 3em')
                span(u' days of logs.')
            with li():
                with span(id='restart'):
                    i(cls='fa fa-refresh')
                    span(u'Restart')
                with span(id='shutdown'):
                    i(cls='fa fa-power-off')
                    span(u'Shutdown')
                with span(u'Current version hash: ', cls='tip'):
                    if core.CURRENT_HASH is not None:
                        a(core.CURRENT_HASH[0:7], href='{}/commits'.format(core.GIT_URL))

        with span(id='save', cat='server'):
            i(cls='fa fa-save')
            span(u'Save Settings')

    @expose
    @settings_page
    def search(self, c):
        h1(u'Search', id='searchform')
        # set the config section at each new section. Just makes everything a little shorter and easier to write.
        c_s = 'Search'
        with ul(id='search', cls='wide'):
            with li(cls='bbord'):
                i(id='searchafteradd', cls='fa fa-square-o checkbox', value=c[c_s]['searchafteradd'])
                span(u'Search immediately after adding movie.')
                span(u'Skips wait until next scheduled search.', cls='tip')
            with li(cls='bbord'):
                i(id='autograb', cls='fa fa-square-o checkbox', value=c[c_s]['autograb'])
                span(u'Automatically grab best result.')
                span(u'Will still wait X days if set.', cls='tip')
            with li(cls='bbord'):
                span(u'Search time:')
                input(type='number', min='0', max='23', id='searchtimehr', style='width: 2.5em', value=c[c_s]['searchtimehr'])
                span(u':')
                input(type='number', min='0', max='59', id='searchtimemin', style='width: 2.5em', value=c[c_s]['searchtimemin'])
                span(u'What time of day to begin searches (24h time). Requires Restart.', cls='tip')
            with li(cls='bbord'):
                span(u'Search every ')
                input(type='number', min='1', id='searchfrequency', style='width: 2.5em', value=c[c_s]['searchfrequency'])
                span(u'hours.')
                span(u'Once releases are available according to predb.me. Requires Restart.', cls='tip')
            with li(cls='bbord'):
                span(u'Wait ')
                input(type='number', min='0', max='14', id='waitdays', style='width: 2.0em', value=c[c_s]['waitdays'])
                span(u' days for best release.')
                span(u'After movie is found, wait to snatch in case better match is found.', cls='tip')
            with li(cls='bbord'):
                i(id='keepsearching', cls='fa fa-square-o checkbox', value=c[c_s]['keepsearching'])
                span(u'Continue searching for ')
                input(type='number', min='0', id='keepsearchingdays', style='width: 2.5em', value=c[c_s]['keepsearchingdays'])
                span(u' days for best release.')
            with li(cls='bbord'):
                span(u'Retention: ')
                input(type='number', min='0', id='retention', value=c[c_s]['retention'])
                span(u' days.')
                span(u'Use 0 for no limit.', cls='tip')
            with li():
                i(id='imdbsync', cls='fa fa-square-o checkbox', value=c[c_s]['imdbsync'])
                span(u'Sync imdb watch list.')
                input(type='text', id='imdbrss', value=c[c_s]['imdbrss'], placeholder="http://rss.imdb.com/list/...", style="width:25em;")
                span(u'*Requires restart. Syncs every 6 hours.', cls='tip')

        with span(id='save', cat='search'):
            i(cls='fa fa-save')
            span(u'Save Settings')

    @expose
    @settings_page
    def quality(self, c):
        span(u'Quality and Filters may be set separately for each movie, this is the '
             'default setting that will be used to \'Quick-Add\' movies.')
        br()
        h1(u'Quality')
        c_s = 'Quality'
        resolutions = ['4K', '1080P', '720P', 'SD']
        with ul(id='quality', cls='wide'):
            # Resolution Block
            with ul(id='resolution', cls='sortable'):
                span(u'Resolutions', cls='sub_cat not_sortable')

                for res in resolutions:
                    prior = '{}priority'.format(res)
                    with li(cls='rbord', id=prior, sort=c[c_s][res][1]):
                        i(cls='fa fa-bars')
                        i(id=res, cls='fa fa-square-o checkbox', value=c[c_s][res][0])
                        span(res)

            # Size restriction block
            with ul(id='resolution_size'):
                li(u'Size Restrictions (MB)', cls='sub_cat')

                for res in resolutions:
                    min = '{}min'.format(res)
                    max = '{}max'.format(res)
                    with li():
                        span(res)
                        input(type='number', id=min, value=c[c_s][res][2], min='0')
                        input(type='number', id=max, value=c[c_s][res][3], min='0')

        div(u','.join(resolutions), cls='hidden_data')

        h1(u'Filters', id='filter_form')
        # set the config section at each new section. Just makes everything a little shorter and easier to write.
        c_s = 'Filters'
        with ul(id='filters', cls='wide'):
            with li(cls='bbord'):
                span(u'Required words:')
                input(type='text', id='requiredwords', value=c[c_s]['requiredwords'])
                span(u'Releases must contain these words.', cls='tip')
            with li(cls='bbord'):
                span(u'Preferred words:')
                input(type='text', id='preferredwords', value=c[c_s]['preferredwords'])
                span(u'Releases with these words score higher.', cls='tip')
            with li():
                span(u'Ignored words:')
                input(type='text', id='ignoredwords', value=c[c_s]['ignoredwords'])
                span(u'Releases with these words are ignored.', cls='tip')

        with span(id='save', cat='quality'):
            i(cls='fa fa-save')
            span(u'Save Settings')

    @expose
    @settings_page
    def providers(self, c):
        h1(u'Indexers')
        c_s = 'Indexers'
        with ul(id='indexers', cls='wide'):
            with li():
                with ul(id='newznab_list'):
                    with li(cls='sub_cat'):
                        span(u'NewzNab Indexers')

                    for n in c[c_s]:
                        with li(cls='newznab_indexer'):
                            i(cls='newznab_check fa fa-square-o checkbox', value=c[c_s][n][2])
                            input(type='text', cls='newznab_url', value=c[c_s][n][0], placeholder=" http://www.indexer-url.com/")
                            input(type='text', cls='newznab_api', value=c[c_s][n][1], placeholder=" Api Key")
                    with li(id='add_newznab_row'):
                        i(cls='fa fa-plus-square', id='add_row')

        with span(id='save', cat='providers'):
            i(cls='fa fa-save')
            span(u'Save Settings')

    @expose
    @settings_page
    def downloader(self, c):
        h1(u'Downloader')
        with ul(id='downloader'):
            c_s = 'Sabnzbd'
            with li(cls='bbord'):
                i(id='sabenabled', cls='fa fa-circle-o radio', tog='sabnzbd', value=c[c_s]['sabenabled'])
                span(u'Sabnzbd', cls='sub_cat')
            # I'm not 100% sure it is valid to do a ul>ul, but it only work this way so deal with it.
            with ul(id='sabnzbd'):
                with li(u'Host & Port: ', cls='bbord'):
                    input(type='text', id='sabhost', value=c[c_s]['sabhost'], style='width: 25%')
                    span(u' : ')
                    input(type='text', id='sabport', value=c[c_s]['sabport'], style='width: 25%')
                with li(u'Api Key: ', cls='bbord'):
                    input(type='text', id='sabapi', value=c[c_s]['sabapi'], style='width: 50%')
                    span(u'Please use full api key.', cls='tip')
                with li(u'Category: ', cls='bbord'):
                    input(type='text', id='sabcategory', value=c[c_s]['sabcategory'], style='width: 50%')
                    span(u'i.e. \'movies\', \'watcher\'. ', cls='tip')
                with li(u'Priority: ', cls='bbord'):
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
                        span(u'Test Connection')
            c_s = 'NzbGet'
            with li():
                i(id='nzbgenabled', cls='fa fa-circle-o radio', tog='nzbget', value=c[c_s]['nzbgenabled'])
                span(u'NZBGet', cls='sub_cat')
            with ul(id='nzbget'):
                with li(u'Host & Port: ', cls='bbord'):
                    input(type='text', id='nzbghost', value=c[c_s]['nzbghost'], style='width: 25%')
                    span(u' : ')
                    input(type='text', id='nzbgport', value=c[c_s]['nzbgport'], style='width: 25%')
                with li(u'User Name: ', cls='bbord'):
                    input(type='text', id='nzbguser', value=c[c_s]['nzbguser'], style='width: 50%')
                    span(u'Default: nzbget.', cls='tip')
                with li(u'Password: ', cls='bbord'):
                    input(type='text', id='nzbgpass', value=c[c_s]['nzbgpass'], style='width: 50%')
                    span(u'Default: tegbzn6789.', cls='tip')
                with li(u'Category: ', cls='bbord'):
                    input(type='text', id='nzbgcategory', value=c[c_s]['nzbgcategory'], style='width: 50%')
                    span(u'i.e. \'movies\', \'watcher\'. ', cls='tip')
                with li(u'Priority: ', cls='bbord'):
                    with select(id='nzbgpriority', style='width: 50%'):
                        pl = ['Very Low', 'Low', 'Normal', 'High', 'Forced']
                        for o in pl:
                            if o == c[c_s]['nzbgpriority']:
                                option(o, value=o, selected="selected")
                            else:
                                option(o, value=o)
                with li(cls='bbord'):
                    i(id='nzbgaddpaused', cls='fa fa-square-o checkbox', value=c[c_s]['nzbgaddpaused'])
                    span(u'Add Paused')

                with li():
                    with span(cls='test_connection', mode='nzbget'):
                        i(cls='fa fa-plug')
                        span(u'Test Connection')

        with span(id='save', cat='downloader'):
            i(cls='fa fa-save')
            span(u'Save Settings')

    @expose
    @settings_page
    def postprocessing(self, c):
        h1(u'Post-Processing')
        c_s = 'Postprocessing'
        with ul(id='postprocessing'):
            with li(cls='bbord'):
                i(id='cleanupfailed', cls='fa fa-square-o checkbox', value=c[c_s]['cleanupfailed'])
                span(u'Delete leftover files after a failed download.')
            with li(cls='bbord'):
                i(id='renamerenabled', cls='fa fa-square-o checkbox', value=c[c_s]['renamerenabled'])
                span(u'Enable Renamer')
            with ul(id='renamer'):
                with li():
                    input(id='renamerstring', type='text', style='width: 80%', value=c[c_s]['renamerstring'], placeholder='{title} ({year}) {resolution}')
                    br()
                    span(u'Example: ')
                    br()
                    span(u'{title} {year} - {videocodec} = How to Train Your Dragon 2010 - x264.mkv',  cls='taglist')

            with li(cls='bbord'):
                i(id='moverenabled', cls='fa fa-square-o checkbox', value=c[c_s]['moverenabled'])
                span(u'Enable Mover')
            with ul(id='mover'):
                with li():
                    span(u'Move movie file to: ')
                    input(type='text', style='width: 28em', id='moverpath', value=c[c_s]['moverpath'])
                    span(u'Use absolute path.', cls='tip')
                    br()
                    span(u'Example: ')
                    br()
                    span(u'/home/user/movies/{title} {year} = /home/user/movies/Black Swan 2010/',  cls='taglist')
                    br()
                    span(u'Move additional files:')
                    input(type='text', style='width: 15em', id='moveextensions', value=c[c_s]['moveextensions'], placeholder='srt, nfo')
                    span(u'Files will be renamed with Renamer settings.', cls='tip')
                    br()
                    i(id='cleanupenabled', cls='fa fa-square-o checkbox', value=c[c_s]['cleanupenabled'])
                    span(u'Clean up after move.')
            with li(u'Replace illegal characters with: ', cls='bbord'):
                input(type='text', id='replaceillegal', value=c[c_s]['replaceillegal'], style='width: 2em')
                span(u'Leave blank to simply remove characters.', cls='tip')
            with li(u'Available tags:'):
                span(u'{title} {year} {resolution} {rated} {imdbid} {videocodec} {audiocodec} {releasegroup} {source}', cls='taglist')

        with span(id='save', cat='postprocessing'):
            i(cls='fa fa-save')
            span(u'Save Settings')

    @expose
    @settings_page
    def about(self, c):
        with div(cls='about'):
            h1(u'About Watcher')

            h2(u'Source')
            with p():
                span(u'Watcher is hosted and maintained on GitHub. You may view the repository at ')
                a(u'https://github.com/', href='https://github.com/nosmokingbandit/watcher')

            h2(u'License')
            with p():
                span(u'''
                    Watcher is open-source and licensed under the Apache 2.0 license. The essence of the
                    Apache 2.0 license is that any user can, for any reason, modify, distribute, or
                    repackage the licesed software with the condition that this license is included with,
                    and remains applicable to, any derivative works. You may not use the Watcher logo
                    or design elements without express approval by the owner. You may not hold the
                    developers of Watcher liable for any damages incurred from use.
                    '''
                     )
            with p():
                span(u'You may view the full, binding license at ')
                a(u'http://www.apache.org/', href='http://www.apache.org/licenses/LICENSE-2.0.html')
                span(u' or in license.txt included in the root folder of Watcher.')
            h2(u'Attribution')
            with p():
                span(u'''
                    Watcher is only possible because of the amazing open-source works that are
                    included in this package. The Watcher license does not apply to these
                    properties. Please check each package's license requirements when using them
                    in your own work.
                    '''
                     )
            with ul(id='libraries'):
                with li():
                    a(u'CherryPy', href='http://cherrypy.org/')
                with li():
                    a(u'SQLAlchemy', href='http://www.sqlalchemy.org/')
                with li():
                    a(u'Six', href='https://pypi.python.org/pypi/six')
                with li():
                    a(u'FuzzWuzzy', href='https://pypi.python.org/pypi/fuzzywuzzy')
                with li():
                    a(u'Font-Awesome', href='http://fontawesome.io/')
                with li():
                    a(u'JQuery', href='https://jquery.com/')
                with li():
                    a(u'Parse Torrent Name', href='https://pypi.python.org/pypi/parse-torrent-name')

    def get_themes(self):
        theme_path = os.path.join(core.PROG_PATH, 'static', 'css')
        themes = []
        for i in os.listdir(theme_path):
            if os.path.isdir(os.path.join(theme_path, i)):
                themes.append(i)
        themes.append(u'Default')
        return themes

# pylama:ignore=W0401
