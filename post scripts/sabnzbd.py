# Disable 'Post-Process Only Verified Jobs' in Sabnzbd.
# Set up Watcher server info.
conf = {
    'watcherkey': 'b9c139de470e62f7d0c1fa3b48ce153a',
    'watcherhost': 'localhost',
    'watcherport': '9090',
    'sabkey': '30d0729ea1e30098f0f79347e988b3a4',
    'sabhost': 'localhost',
    'sabport': '8080'
}


import sys
import os
import urllib2
import json

try:
    status = int(sys.argv[7])
    guid =  sys.argv[3].replace('-', ':').replace('+', '/')
except:
    print 'Post-processing failed. Incorrect args.'
    sys.exit(1)

watcherkey = conf['watcherkey']
watcherhost = conf['watcherhost']
watcherport = conf['watcherport']
sabkey = conf['sabkey']
sabhost = conf['sabhost']
sabport = conf['sabport']


# get guid from sab history: ## why do we do this?
name = urllib2.quote(sys.argv[3])
url = 'http://{}:{}/sabnzbd/api?apikey={}&mode=history&output=json&search={}'.format(sabhost, sabport, sabkey, name)

request = urllib2.Request(url, headers={'User-Agent' : 'Mozilla/5.0'} )
response = urllib2.urlopen(request).read()

slots = json.loads(response)['history']['slots']

for dl in slots:
    if dl['loaded'] == True:
        guid = dl['url']
        break

if not guid:
    print 'Download GUID not found.'
    sys.exit(1)

guid = urllib2.quote(guid, safe='')
path = urllib2.quote(sys.argv[1], safe='')

# send it to Watcher
if status == 0: # finished ok.
    mode = 'complete'

    url = 'http://{}:{}/api/apikey={}&mode={}&guid={}&path={}'.format(watcherhost, watcherport, watcherkey, mode, guid, path)
    request = urllib2.Request(url, headers={'User-Agent' : 'Mozilla/5.0'} )
    response = urllib2.urlopen(request).read()

    if response == 'Success':
        sys.exit(0)
    else:
        sys.exit(1)

if status != 0: # anything less than zero is an error.
    mode = 'failed'
    url = 'http://{}:{}/api/apikey={}&mode={}&guid={}'.format(watcherhost, watcherport, watcherkey, mode, guid)
    request = urllib2.Request(url, headers={'User-Agent' : 'Mozilla/5.0'} )
    response = urllib2.urlopen(request).read()
    if response == 'Success':
        sys.exit(0)
    else:
        sys.exit(1)
