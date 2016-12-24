#!/usr/bin/env python

##########################################
######## DO NOT MODIFY THIS FILE! ########
## CONFIGURE API INFO THROUGH NZBGET UI ##
##########################################

#####################################
### NZBGET POST-PROCESSING SCRIPT ###

# Script to send post-processing info
# to Watcher.

#####################################
### OPTIONS                       ###

# Watcher API key.
#Apikey=

# Watcher address.
#Host=http://localhost:9090/

### NZBGET POST-PROCESSING SCRIPT ###
#####################################

import json
import os
import sys
import urllib2

POSTPROCESS_SUCCESS = 93
POSTPROCESS_ERROR = 94
POSTPROCESS_NONE = 95


watcheraddress = os.environ['NZBPO_ADDRESS']
watcherapi = os.environ['NZBPO_APIKEY']
name = os.environ['NZBPP_NZBNAME']

# The values are are going to try to get:
downloadid = ''
guid = ''
path = ''

downloadid = os.environ['NZBPP_NZBID']

# can be blank it from an uploaded nzb file
if os.environ['NZBPP_URL']:
    # since it is a path it must be encoded to send via GET
    guid = urllib2.quote(os.environ['NZBPP_URL'], safe='')

path = urllib2.quote(os.environ['NZBPP_DIRECTORY'], safe='')

# set the post-processing mode
if os.environ['NZBPP_TOTALSTATUS'] == 'SUCCESS':
    print 'Sending {} to Watcher as Complete.'.format(name)
    mode = 'complete'
else:
    print 'Sending {} to Watcher as Failed.'.format(name)
    mode = 'failed'

# send it to watcher
url = '{}/postprocessing?apikey={}&mode={}&guid={}&downloadid={}&path={}'.format(watcheraddress, watcherapi, mode, guid, downloadid, path)
request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = json.loads(urllib2.urlopen(request).read())

if response['status'] == 'finished':
    sys.exit(POSTPROCESS_SUCCESS)
elif response['status'] == 'incomplete':
    sys.exit(POSTPROCESS_ERROR)
else:
    sys.exit(POSTPROCESS_NONE)
