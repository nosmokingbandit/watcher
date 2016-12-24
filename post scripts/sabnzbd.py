#!/usr/bin/env python

# ======================================== #
# ============= INSTRUCTIONS ============= #

# Disable 'Post-Process Only Verified Jobs' in Sabnzbd.
# Add api information to conf:

conf = {
    'watcherapi': 'WATCHERAPIKEY',
    'watcheraddress': 'http://localhost:9090/',
    'sabkey': 'SABAPIKEY',
    'sabhost': 'localhost',
    'sabport': '8080'
}

#  DO NOT TOUCH ANYTHING BELOW THIS LINE!  #
# ======================================== #

import json
import sys
import urllib2

try:
    status = int(sys.argv[7])
    guid = sys.argv[3].replace('-', ':').replace('+', '/')
except:
    print 'Post-processing failed. Incorrect args.'
    sys.exit(1)

watcherhost = conf['watcherhost']
watcherport = conf['watcherport']
watcherapi = conf['watcherkey']
sabkey = conf['sabkey']
sabhost = conf['sabhost']
sabport = conf['sabport']


# get guid and nzo_id from sab history:
name = urllib2.quote(sys.argv[3], safe='')
url = 'http://{}:{}/sabnzbd/api?apikey={}&mode=history&output=json&search={}'.format(sabhost, sabport, sabkey, name)

request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = urllib2.urlopen(request).read()

slots = json.loads(response)['history']['slots']

for dl in slots:
    if dl['loaded'] is True:
        guid = dl['url']
        downloadid = dl['nzo_id']
        break

if not guid:
    print 'Download GUID not found.'
    sys.exit(1)


# prep all other params
guid = urllib2.quote(guid, safe='')
path = urllib2.quote(sys.argv[1], safe='')

# send it to Watcher
if status == 0:
    print 'Seinding {} to Watcher as Complete.'.format(name)
    mode = 'complete'
else:
    print 'Seinding {} to Watcher as Failed.'.format(name)
    mode = 'failed'

url = 'http://{}:{}/postprocessing?apikey={}&mode={}&guid={}&downloadid={}&path={}'.format(watcherhost, watcherport, watcherapi, mode, guid, downloadid, path)
request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = json.loads(urllib2.urlopen(request).read())

if response['status'] == 'finished':
    sys.exit(0)
else:
    sys.exit(1)
