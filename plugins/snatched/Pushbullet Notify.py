# Watcher Plugin to send Pushbullet Notifications
# Trigger: Snatched Release

import sys
import json
import urllib2
from time import strftime

script, title, year, imdbid, resolution, kind, downloader, indexer, info_link, conf_json = sys.argv
conf = json.loads(conf_json)
apikey = conf['Api Key']

pushbullet_api = 'https://api.pushbullet.com/v2/pushes'
headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + apikey}

body = {'type': 'link',
        'title': 'Watcher Snatched {}'.format(title),
        'body': '{} sent to {} on {}.'.format(title, downloader, strftime("%a, %b %d, at %I:%M%p")),
        'url': urllib2.unquote(info_link)
        }

if conf.get('Send to Device Identifier'):
    body['device_iden'] = conf['Send to Device Identifier']

if conf['Send Using Channel']:
    body['channel_tag'] = conf['Send Using Channel']

body = json.dumps(body)

request = urllib2.Request(pushbullet_api, body, headers)

try:
    response = urllib2.urlopen(request)
    print response.read()
except Exception, e:
    print str(e)
    sys.exit(1)

sys.exit(0)
