#!/usr/bin/env python

###########################################
### NZBGET POST-PROCESSING SCRIPT       ###

# Script to send post-processing info
# to Watcher.


###########################################
### OPTIONS                  ###

# Watcher API key.
#Apikey=

# Watcher host.
#Host=localhost

# Watcher port.
#Port=9090


### NZBGET POST-PROCESSING SCRIPT       ###
###########################################
import os
import sys
import urllib2


POSTPROCESS_SUCCESS=93
POSTPROCESS_ERROR=94
POSTPROCESS_NONE=95


watcherhost = os.environ['NZBPO_HOST']
watcherport = os.environ['NZBPO_PORT']
watcherapi = os.environ['NZBPO_APIKEY']

# since it is a link it must be encoded to send via GET

if os.environ['NZBPP_URL']:
    guid = urllib2.quote(os.environ['NZBPP_URL'], safe='')
else:
    guid = 'None'

path = urllib2.quote(os.environ['NZBPP_DIRECTORY'], safe='')

# send it to Watcher
if os.environ['NZBPP_TOTALSTATUS'] == 'SUCCESS':
    print 'Sending {} to Watcher as Complete.'.format(os.environ['NZBPP_NZBNAME'])
    mode = 'complete'

    url = 'http://{}:{}/api/apikey={}&mode={}&guid={}&path={}'.format(watcherhost, watcherport, watcherapi, mode, guid, path)

    request = urllib2.Request(url, headers={'User-Agent' : 'Mozilla/5.0'} )
    response = urllib2.urlopen(request).read()
    if response == 'Success':
        sys.exit(POSTPROCESS_SUCCESS)
    elif response == 'None':
        sys.exit(POSTPROCESS_NONE)
    else:
        sys.exit(POSTPROCESS_ERROR)


else:
    print 'Sending {} to Watcher as Failed.'.format(os.environ['NZBPP_NZBNAME'])
    mode = 'failed'
    url = 'http://{}:{}/api/apikey={}&mode={}&guid={}&path={}'.format(watcherhost, watcherport, watcherapi, mode, guid, path)
    request = urllib2.Request(url, headers={'User-Agent' : 'Mozilla/5.0'} )
    response = urllib2.urlopen(request)
    if response == 'Success':
        sys.exit(POSTPROCESS_SUCCESS)
    else:
        sys.exit(POSTPROCESS_ERROR)

sys.exit(POSTPROCESS_NONE)
