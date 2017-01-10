# coding=utf-8

import urllib
import urllib2

watcheraddress = u'http://localhost:9090/watcher/'

url = u'{}/postprocessing/'.format(watcheraddress)


apikey = '4c0c7699d7389a7d062a713a107b327c'

mode = 'failed'

guid = u'https://newztown.co.za/getnzb/7495a7b70de20a7ebffc1e625d03b434.nzb&i=46049&r=c8dace4f8dd764fa94fe793f557ebd7d'

downloadid = 'downloadid_1234'

path = path = u"C:\\Users\\Steven\\Desktop\\WALL·E.2008.1080.bluray.dts-NoGroup - Copy".encode('utf-8')


data = {
    'apikey': apikey,
    'mode': mode,
    'guid': guid,
    'downloadid': downloadid,
    'path': path
}

post_data = urllib.urlencode(data)

request = urllib2.Request(url, post_data)

response = urllib2.urlopen(request)
print response.read()
