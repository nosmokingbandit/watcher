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
    url = 'http://{}:{}/api/apikey={}&mode={}&guid={}'.format(watcherhost, watcherport, watcherapi, mode, guid)
    request = urllib2.Request(url, headers={'User-Agent' : 'Mozilla/5.0'} )
    response = urllib2.urlopen(request)
    if response == 'Success':
        sys.exit(POSTPROCESS_SUCCESS)
    else:
        sys.exit(POSTPROCESS_ERROR)


'''


Watcher:

{
'NZBOP_CATEGORY3_UNPACK': 'yes',
'TMP': 'C:\\Users\\Steven\\AppData\\Local\\Temp',
'NZBOP_SERVER1_GROUP': '0',
'NZBPP_QUEUEDFILE': 'C:\\Users\\Steven\\Downloads\\nzb\\Robot.Chicken.Star.Wars.Special.DVDRip.XviD-SAiNTS.nzb.queued',
'NZBOP_DEBUGTARGET': 'log',
'NZBOP_DOWNLOADRATE': '0',
'NZBOP_WATCHER_PY_PORT': '9090',
'NZBOP_CATEGORY2.ALIASES': '',
'PROCESSOR_IDENTIFIER': 'Intel64 Family 6 Model 60 Stepping 3, GenuineIntel',
'NZBOP_LOCKFILE': 'C:\\Program Files (x86)\\NZBGet/nzbget.lock',
'NZBOP_EVENTINTERVAL': '0',
'NZBOP_FEEDSCRIPT': '',
'NZBOP_APPDIR': 'C:\\Program Files (x86)\\NZBGet',
'NZBOP_CATEGORY4.POSTSCRIPT': '',
'NZBOP_DESTDIR': 'C:\\Users\\Steven\\Downloads',
'NZBOP_ROTATELOG': '3',
'SYSTEMROOT': 'C:\\WINDOWS',
'NZBOP_DUPECHECK': 'yes',
'NZBOP_WATCHER.PY:HOST': 'localhost',
'NZBOP_EMAIL_PY_SENDMAIL': 'Always',
'NZBOP_PARPAUSEQUEUE': 'no',
'NZBOP_SAVEQUEUE': 'yes',
'NZBPP_NZBFILENAME': 'Robot.Chicken.Star.Wars.Special.DVDRip.XviD-SAiNTS.nzb',
'NZBOP_WRITEBUFFER': '1024',
'NZBOP_REQUIREDDIR': '',
'NZBPR_WATCHER_PY_': 'yes',
'NZBOP_EMAIL_PY_ENCRYPTION': 'yes',
'NZBOP_SERVER1.CONNECTIONS': '8',
'NZBOP_CATEGORY4_DESTDIR': '',
'NZBOP_CATEGORY1.ALIASES': '',
'NZBPR_WATCHER.PY:': 'yes',
'NZBOP_TERMINATETIMEOUT': '600',
'NZBOP_DIRECTWRITE': 'yes',
'NZBOP_SERVER1_PORT': '563',
'NZBOP_EMAIL_PY_TO': 'myaccount@gmail.com',
'NZBOP_CONTROLIP': '0.0.0.0',
'NZBOP_EMAIL_PY_FILELIST': 'yes',
'NZBOP_CATEGORY2.NAME': 'Series',
'NZBOP_SERVER1.CIPHER': '',
'NZBOP_CATEGORY1_DESTDIR': '',
'NZBOP_CATEGORY1_ALIASES': '',
'WINDIR': 'C:\\WINDOWS',
'NZBOP_RESTRICTEDUSERNAME': '',
'NZBOP_SERVER1.HOST': 'news.cheapnews.eu',
'NZBOP_CONTROLPASSWORD': 'tegbzn',
'NZBOP_PARSCAN': 'extended',
'FPS_BROWSER_APP_PROFILE_STRING': 'Internet Explorer',
'NZBOP_SERVER1.GROUP': '0',
'NZBOP_CONTINUEPARTIAL': 'yes',
'NZBOP_PARTIMELIMIT': '0',
'NZBOP_DETAILTARGET': 'log',
'NZBOP_HEALTHCHECK': 'delete',
'NZBOP_UNPACK': 'yes',
'NZBOP_PARREPAIR': 'yes',
'NZBOP_ARTICLECACHE': '250',
'NZBOP_KEEPHISTORY': '30',
'NZBOP_CATEGORY2_UNPACK': 'yes',
'NZBOP_UNPACKCLEANUPDISK': 'yes',
'NZBOP_INFOTARGET': 'both',
'HOMEDRIVE': 'C:',
'NZBOP_CONTROLUSERNAME': 'nzbget',
'NZBOP_RETRIES': '3',
'NZBOP_QUEUEDIR': 'C:\\ProgramData\\NZBGet\\queue',
'NZBPP_CATEGORY': 'Movies',
'NZBOP_CRCCHECK': 'yes',
'NZBOP_CATEGORY1_POSTSCRIPT': 'Watcher.py',
'NZBOP_CATEGORY4_UNPACK': 'yes',
'NZBPR__DNZB_DETAILS': 'https://6box.me/details/837f528f7c4e6efcaf1887850c6719f5',
'NZBOP_EMAIL.PY:TO': 'myaccount@gmail.com',
'PROCESSOR_LEVEL': '6',
'NZBOP_UNPACKPAUSEQUEUE': 'no',
'NZBOP_CATEGORY4_POSTSCRIPT': '',
'NZBPP_SERVER1_FAILEDARTICLES': '82',
'NZBOP_SERVER1.OPTIONAL': 'no',
'NZBOP_CATEGORY1.POSTSCRIPT': 'Watcher.py',
'LOCALAPPDATA': 'C:\\Users\\Steven\\AppData\\Local',
'NZBOP_SCRIPTORDER': '',
'NZBOP_NZBDIRFILEAGE': '60',
'NZBPR__DNZB_NAME': 'Robot.Chicken.Star.Wars.Special.DVDRip.XviD-SAiNTS',
'NZBOP_PARCHECK': 'auto',
'NZBOP_ERRORTARGET': 'both',
'NZBOP_DECODE': 'yes',
'NZBOP_SERVER1_NAME': 'CheapNews',
'NZBOP_PARQUICK': 'yes',
'NZBOP_EMAIL_PY_PASSWORD': 'mypass',
'NZBOP_FLUSHQUEUE': 'yes',
'NZBPR_*DNZB:MOREINFO': 'http://www.imdb.com/title/tt1020990',
'NZBOP_RELOADQUEUE': 'yes',
'NZBPP_NZBID': '100',
'NZBOP_WATCHER_PY_APIKEY': 'd1b2379cac3c261cbd20cfb9dcfe1f6d',
'NZBOP_CATEGORY4.ALIASES': '',
'NZBOP_ACCURATERATE': 'no',
'NZBOP_CURSESNZBNAME': 'yes',
'NZBPP_UNPACKSTATUS': '0',
'NZBPP_DIRECTORY': 'C:\\Users\\Steven\\Downloads\\tmp\\Robot.Chicken.Star.Wars.Special.DVDRip.XviD-SAiNTS.#101',
'NZBOP_CATEGORY1.NAME': 'Movies',
'NZBOP_CATEGORY1_NAME': 'Movies',
'COMMONPROGRAMFILES(X86)': 'C:\\Program Files (x86)\\Common Files',
'NZBOP_SERVER1.RETENTION': '0',
'NZBOP_AUTHORIZEDIP': '127.0.0.1',
'NZBOP_CATEGORY2_NAME': 'Series',
'NZBOP_EMAIL.PY:PORT': '25',
'NZBPP_CRITICALHEALTH': '895',
'NZBOP_SERVER1_ACTIVE': 'yes',
'FPS_BROWSER_USER_PROFILE_STRING': 'Default',
'HOMEPATH': '\\Users\\Steven',
'NZBOP_EMAIL.PY:PASSWORD': 'mypass',
'NZBOP_CATEGORY2_ALIASES': '',
'NZBOP_WATCHER.PY:PORT': '9090',
'NZBOP_SERVER1.NAME': 'CheapNews',
'NZBOP_ADDUSERNAME': '',
'LOGONSERVER': '\\\\STEVEN-DESKTOP',
'NZBOP_CATEGORY3.UNPACK': 'yes',
'NZBOP_PARRENAME': 'yes',
'NZBOP_QUEUESCRIPT': '',
'NZBPP_SERVER1_SUCCESSARTICLES': '0',
'NZBOP_CATEGORY4.DESTDIR': '',
'PROCESSOR_ARCHITEW6432': 'AMD64',
'NZBOP_OUTPUTMODE': 'ncurses',
'ALLUSERSPROFILE': 'C:\\ProgramData',
'NZBOP_PARBUFFER': '250',
'NZBOP_VERSION': '17.1',
'NZBOP_EMAIL.PY:NZBLOG': 'OnFailure',
'NZBOP_CATEGORY2_DESTDIR': '',
'NZBPR_*DNZB:NAME': 'Robot.Chicken.Star.Wars.Special.DVDRip.XviD-SAiNTS',
'NZBPP_DUPEKEY': 'tt1020990',
'NZBOP_SCRIPTDIR': 'C:\\ProgramData\\NZBGet\\scripts',
'ASL.LOG': 'Destination=file',
'NZBOP_EMAIL.PY:FILELIST': 'yes',
'NZBPP_SUCCESSARTICLES': '0',
'NZBOP_EMAIL_PY_PORT': '25',
'NZBOP_LOGFILE': 'C:\\ProgramData\\NZBGet\\nzbget.log',
'NZBOP_TIMECORRECTION': '0',
'APPDATA': 'C:\\Users\\Steven\\AppData\\Roaming',
'OS': 'Windows_NT',
'NZBOP_DAILYQUOTA': '0',
'NZBPR_*DNZB:DETAILS': 'https://6box.me/details/837f528f7c4e6efcaf1887850c6719f5',
'PUBLIC': 'C:\\Users\\Public',
'NZBOP_CATEGORY3.DESTDIR': '',
'NZBOP_CATEGORY1_UNPACK': 'yes',
'NZBOP_URLFORCE': 'yes',
'NZBOP_EMAIL.PY:FROM': '"NZBGet" <myaccount@gmail.com>',
'NZBOP_FEEDHISTORY': '7',
'NZBOP_SERVER1_ENCRYPTION': 'yes',
'NZBOP_SERVER1_OPTIONAL': 'no',
'NZBOP_SECURECERT': '',
'NZBPR__DNZB_MOVIEYEAR': '2007',
'NZBOP_SECUREPORT': '6791',
'NZBOP_UMASK': '1000',
'COMPUTERNAME': 'STEVEN-DESKTOP',
'NZBPP_FAILEDARTICLES': '82',
'NZBOP_EMAIL.PY:SENDMAIL': 'Always',
'USERDOMAIN': 'STEVEN-DESKTOP',
'NZBPR_*UNPACK:': 'yes',
'NZBOP_CATEGORY3_DESTDIR': '',
'NZBOP_EMAIL.PY:SERVER': 'smtp.gmail.com',
'NZBOP_RESTRICTEDPASSWORD': '',
'COMMONPROGRAMFILES': 'C:\\Program Files (x86)\\Common Files',
'NZBOP_SERVER1_PASSWORD': 'bitemyshinymetalass1',
'NZBOP_CURSESTIME': 'no',
'NZBOP_SERVER1.LEVEL': '0',
'NZBOP_RETRYINTERVAL': '10',
'NZBPR_*DNZB:NFO': 'https://6box.me/api?t=getnfo&id=837f528f7c4e6efcaf1887850c6719f5&raw=1&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
'NZBOP_CATEGORY2.DESTDIR': '',
'NZBOP_EMAIL_PY_NZBLOG': 'OnFailure',
'NZBOP_EMAIL_PY_FROM': '"NZBGet" <myaccount@gmail.com>',
'NZBOP_SERVER1_CONNECTIONS': '8',
'NZBOP_MONTHLYQUOTA': '0',
'NZBOP_SEVENZIPCMD': '7z',
'PROCESSOR_ARCHITECTURE': 'x86',
'NZBOP_TEMPDIR': 'C:\\ProgramData\\NZBGet\\tmp',
'NZBPP_NZBNAME': 'Robot.Chicken.Star.Wars.Special.DVDRip.XviD-SAiNTS',
'NZBOP_SCRIPTPAUSEQUEUE': 'no',
'NZBOP_WRITELOG': 'append',
'NZBOP_EMAIL.PY:BROKENLOG': 'yes',
'USERDOMAIN_ROAMINGPROFILE': 'STEVEN-DESKTOP',
'NZBOP_PARTHREADS': '0',
'PROGRAMW6432': 'C:\\Program Files',
'USERNAME': 'Steven',
'NZBOP_EMAIL_PY_SERVER': 'smtp.gmail.com',
'NZBOP_URLCONNECTIONS': '4',
'NZBOP_CATEGORY3.ALIASES': '',
'NZBOP_UPDATEINTERVAL': '200',
'NZBOP_SERVER1.PASSWORD': 'bitemyshinymetalass1',
'NZBOP_SERVER1_HOST': 'news.cheapnews.eu',
'NZBOP_POSTSCRIPT': '',
'NZBPP_DUPEMODE': 'ALL',
'NZBPP_FINALDIR': '',
'NZBOP_CATEGORY3.POSTSCRIPT': '',
'NZBOP_CATEGORY2_POSTSCRIPT': '',
'NZBPP_HEALTH': '894',
'NZBOP_CATEGORY3_POSTSCRIPT': '',
'NZBOP_EMAIL.PY:STATISTICS': 'yes',
'NZBOP_SERVER1.USERNAME': 'nosmokingbandit',
'PATHEXT': '.COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC',
'NZBOP_NZBCLEANUPDISK': 'yes',
'NZBOP_SERVER1.ACTIVE': 'yes',
'NZBPR__DNZB_PROPERNAME': 'Robot Chicken: Star Wars',
'NZBOP_SHELLOVERRIDE': '',
'NZBPP_SCRIPTSTATUS': 'NONE',
'NZBOP_CATEGORY4.NAME': 'Software',
'NZBOP_NZBDIRINTERVAL': '5',
'NZBOP_DAEMONUSERNAME': 'root',
'NZBPP_PARSTATUS': '1',
'NZBOP_LOGBUFFERSIZE': '1000',
'NZBOP_EMAIL.PY:USERNAME': 'myaccount',
'NUMBER_OF_PROCESSORS': '8',
'NZBOP_SECUREKEY': '',
'NZBOP_CATEGORY4_NAME': 'Software',
'NZBPO_HOST': 'localhost',
'NZBOP_CONFIGFILE': 'C:\\ProgramData\\NZBGet\\nzbget.conf',
'NZBPP_TOTALARTICLES': '837',
'NZBOP_SERVER1_RETENTION': '0',
'NZBPR_*DNZB:MOVIEYEAR': '2007',
'NZBOP_APPBIN': 'C:\\Program Files (x86)\\NZBGet\\nzbget.exe',
'NZBOP_UNRARCMD': 'C:\\Program Files (x86)\\NZBGet\\unrar.exe',
'NZBPP_URL': 'https://6box.me/getnzb/837f528f7c4e6efcaf1887850c6719f5.nzb&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
'NZBOP_CONFIGTEMPLATE': 'C:\\Program Files (x86)\\NZBGet\\nzbget.conf.template',
'USERPROFILE': 'C:\\Users\\Steven',
'NZBOP_SERVER1.PORT': '563',
'PSMODULEPATH': 'C:\\Program Files\\WindowsPowerShell\\Modules;C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\Modules',
'NZBOP_PROPAGATIONDELAY': '0',
'VS140COMNTOOLS': 'C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\Common7\\Tools\\',
'PROCESSOR_REVISION': '3c03',
'NZBOP_CATEGORY4_ALIASES': '',
'NZBOP_NZBLOG': 'yes',
'NZBOP_DUMPCORE': 'no',
'SYSTEMDRIVE': 'C:',
'NZBOP_CATEGORY2.UNPACK': 'yes',
'NZBOP_EMAIL_PY_BROKENLOG': 'yes',
'NZBOP_NZBDIR': 'C:\\Users\\Steven\\Downloads\\nzb',
'NZBOP_CATEGORY1.DESTDIR': '',
'NZBOP_INTERDIR': 'C:\\Users\\Steven\\Downloads\\tmp',
'PROGRAMFILES': 'C:\\Program Files (x86)',
'NZBOP_BROKENLOG': 'yes',
'NZBOP_SCANSCRIPT': '',
'PATH': 'c:\\windows\\system32;c:\\windows;c:\\windows\\system32\\wbem;c:\\windows\\system32\\windowspowershell\\v1.0\\;c:\\program files (x86)\\calibre2\\;c:\\program files (x86)\\freearc\\bin;c:\\adb;C:\\WINDOWS\\system32;C:\\WINDOWS;C:\\WINDOWS\\system32\\wbem;C:\\WINDOWS\\system32\\windowspowershell\\v1.0\\;C:\\Program Files (x86)\\NVIDIA Corporation\\PhysX\\Common;C:\\Python27;C:\\Program Files (x86)\\Brackets\\command;C:\\Program Files (x86)\\FreeArc\\bin;C:\\Users\\Steven\\AppData\\Local\\Microsoft\\WindowsApps;C:\\Python27\\Scripts\\',
'NZBOP_WEBDIR': 'C:\\Program Files (x86)\\NZBGet\\webui',
'COMSPEC': 'C:\\WINDOWS\\system32\\cmd.exe',
'NZBOP_SERVER1_LEVEL': '0',
'NZBOP_CATEGORY3_NAME': 'Music',
'NZBOP_EMAIL.PY:ENCRYPTION': 'yes',
'NZBOP_CATEGORY3.NAME': 'Music',
'NZBOP_WATCHER_PY_HOST': 'localhost',
'NZBOP_SECURECONTROL': 'no',
'NZBOP_CURSESGROUP': 'no',
'NZBPP_STATUS': 'FAILURE/HEALTH',
'NZBPR__UNPACK_': 'yes',
'NZBPR__DNZB_MOREINFO': 'http://www.imdb.com/title/tt1020990',
'NZBOP_EXTCLEANUPDISK': '.par2, .sfv, _brokenlog.txt',
'NZBPR__DNZB_NFO': 'https://6box.me/api?t=getnfo&id=837f528f7c4e6efcaf1887850c6719f5&raw=1&i=8410&r=c73e2d449973cd0aca769007ce4d2b51',
'NZBOP_URLTIMEOUT': '60',
'NZBPO_PORT': '9090',
'SESSIONNAME': 'Console',
'NZBPP_TOTALSTATUS': 'FAILURE',
'NZBOP_CATEGORY4.UNPACK': 'yes',
'NZBOP_SERVER1.JOINGROUP': 'no',
'NZBOP_ARTICLETIMEOUT': '60',
'NZBOP_DISKSPACE': '250',
'PROGRAMDATA': 'C:\\ProgramData',
'NZBOP_SERVER1_USERNAME': 'nosmokingbandit',
'NZBOP_WARNINGTARGET': 'both',
'NZBPO_APIKEY': 'd1b2379cac3c261cbd20cfb9dcfe1f6d',
'NZBOP_EMAIL_PY_USERNAME': 'myaccount',
'NZBOP_CONTROLPORT': '6789',
'NZBOP_CATEGORY3_ALIASES': '',
'NZBOP_UNPACKPASSFILE': '',
'NZBOP_PARIGNOREEXT': '.sfv, .nzb, .nfo',
'NZBOP_WATCHER.PY:APIKEY': 'd1b2379cac3c261cbd20cfb9dcfe1f6d',
'COMMONPROGRAMW6432': 'C:\\Program Files\\Common Files',
'NZBPR_*DNZB:PROPERNAME': 'Robot Chicken: Star Wars',
'TEMP': 'C:\\Users\\Steven\\AppData\\Local\\Temp',
'NZBPP_DUPESCORE': '7009',
'NZBOP_CATEGORY1.UNPACK': 'yes',
'NZBOP_APPENDCATEGORYDIR': 'yes',
'NZBOP_SERVER1.ENCRYPTION': 'yes',
'NZBOP_MAINDIR': 'C:\\ProgramData\\NZBGet',
'NZBOP_EMAIL_PY_STATISTICS': 'yes',
'NZBOP_SERVER1_CIPHER': '',
'NZBPP_HEALTHDELETED': '1',
'NZBOP_SERVER1_JOINGROUP': 'no',
'NZBOP_CATEGORY2.POSTSCRIPT': '',
'PROGRAMFILES(X86)': 'C:\\Program Files (x86)',
'NZBOP_QUOTASTARTDAY': '1',
'NZBOP_ADDPASSWORD': ''
}


'''

'''
history OUTPUT
[

{'NZBName': 'Robot.Chicken.Star.Wars.Special.DVDRip.XviD-SAiNTS', 'Category': 'Movies', 'DeleteStatus': 'HEALTH', 'Log'
: [], 'Parameters': [{'Name': '*Unpack:', 'Value': 'yes'}, {'Name': 'Watcher.py:', 'Value': 'yes'}], 'MoveStatus': 'NONE
', 'UnpackStatus': 'NONE', 'MinPostTime': 1265324382, 'ParTimeSec': 0, 'Health': 894, 'PostTotalTimeSec': 0, 'SuccessArt
icles': 0, 'FileCount': 22, 'ExParStatus': 'NONE', 'Status': 'FAILURE/HEALTH', 'FileSizeMB': 201, 'Deleted': True, 'Extr
aParBlocks': 0, 'ID': 78, 'DupeKey': 'tt1020990', 'MaxPostTime': 1265324759, 'MarkStatus': 'NONE', 'NZBID': 78, 'ScriptS
tatuses': [{'Status': 'NONE', 'Name': 'Watcher.py'}], 'CriticalHealth': 895, 'DownloadedSizeHi': 0, 'Kind': 'NZB', 'Fail
edArticles': 82, 'Name': 'Robot.Chicken.Star.Wars.Special.DVDRip.XviD-SAiNTS', 'MessageCount': 756, 'URL': '', 'Download
TimeSec': 6, 'DestDir': 'C:\\Users\\Steven\\Downloads\\tmp\\Robot.Chicken.Star.Wars.Special.DVDRip.XviD-SAiNTS.#78', 'Fi
leSizeLo': 211129185, 'DownloadedSizeMB': 0, 'NZBFilename': 'Robot.Chicken.Star.Wars.Special.DVDRip.XviD-SAiNTS', 'DupeS
core': 7009, 'FinalDir': '', 'FileSizeHi': 0, 'HistoryTime': 1477522293, 'DownloadedSizeLo': 6098, 'RepairTimeSec': 0, '
UnpackTimeSec': 0, 'ServerStats': [{'ServerID': 1, 'FailedArticles': 82, 'SuccessArticles': 0}], 'TotalArticles': 837, '
NZBNicename': 'Robot.Chicken.Star.Wars.Special.DVDRip.XviD-SAiNTS', 'UrlStatus': 'NONE', 'RemainingFileCount': 0, 'Scrip
tStatus': 'NONE', 'DupeMode': 'ALL', 'ParStatus': 'NONE', 'RetryData': False}, {'NZBName': 'How.To.Train.Your.Dragon.201
0.DVDRip.XviD-TASTE', 'Category': 'Movies', 'DeleteStatus': 'MANUAL', 'Log': [], 'Parameters': [{'Name': '*Unpack:', 'Va
lue': 'yes'}], 'MoveStatus': 'NONE', 'UnpackStatus': 'NONE', 'MinPostTime': 1475440903, 'ParTimeSec': 0, 'Health': 1000,
 'PostTotalTimeSec': 0, 'SuccessArticles': 0, 'FileCount': 62, 'ExParStatus': 'NONE', 'Status': 'DELETED/MANUAL', 'FileS
izeMB': 794, 'Deleted': True, 'ExtraParBlocks': 0, 'ID': 77, 'DupeKey': 'tt0892769', 'MaxPostTime': 1475440903, 'MarkSta
tus': 'NONE', 'NZBID': 77, 'ScriptStatuses': [], 'CriticalHealth': 894, 'DownloadedSizeHi': 0, 'Kind': 'NZB', 'FailedArt
icles': 0, 'Name': 'How.To.Train.Your.Dragon.2010.DVDRip.XviD-TASTE', 'MessageCount': 65, 'URL': '', 'DownloadTimeSec':
0, 'DestDir': 'C:\\Users\\Steven\\Downloads\\tmp\\How.To.Train.Your.Dragon.2010.DVDRip.XviD-TASTE.#77', 'FileSizeLo': 83
3367504, 'DownloadedSizeMB': 0, 'NZBFilename': 'How.To.Train.Your.Dragon.2010.DVDRip.XviD-TASTE ', 'DupeScore': 7010, 'F
inalDir': '', 'FileSizeHi': 0, 'HistoryTime': 1476982979, 'DownloadedSizeLo': 0, 'RepairTimeSec': 0, 'UnpackTimeSec': 0,
 'ServerStats': [], 'TotalArticles': 2153, 'NZBNicename': 'How.To.Train.Your.Dragon.2010.DVDRip.XviD-TASTE', 'UrlStatus'
: 'NONE', 'RemainingFileCount': 0, 'ScriptStatus': 'NONE', 'DupeMode': 'ALL', 'ParStatus': 'NONE', 'RetryData': False},
{'NZBName': 'How.To.Train.Your.Dragon.2010.iNTERNAL.BDRip.x264-EXViDiNT', 'Category': 'Movies', 'DeleteStatus': 'MANUAL'
, 'Log': [], 'Parameters': [{'Name': '*Unpack:', 'Value': 'yes'}], 'MoveStatus': 'NONE', 'UnpackStatus': 'NONE', 'MinPos
tTime': 1396798832, 'ParTimeSec': 0, 'Health': 1000, 'PostTotalTimeSec': 0, 'SuccessArticles': 0, 'FileCount': 32, 'ExPa
rStatus': 'NONE', 'Status': 'DELETED/MANUAL', 'FileSizeMB': 924, 'Deleted': True, 'ExtraParBlocks': 0, 'ID': 76, 'DupeKe
y': 'tt0892769', 'MaxPostTime': 1396798887, 'MarkStatus': 'NONE', 'NZBID': 76, 'ScriptStatuses': [], 'CriticalHealth': 9
48, 'DownloadedSizeHi': 0, 'Kind': 'NZB', 'FailedArticles': 0, 'Name': 'How.To.Train.Your.Dragon.2010.iNTERNAL.BDRip.x26
4-EXViDiNT', 'MessageCount': 35, 'URL': '', 'DownloadTimeSec': 0, 'DestDir': 'C:\\Users\\Steven\\Downloads\\tmp\\How.To.
Train.Your.Dragon.2010.iNTERNAL.BDRip.x264-EXViDiNT.#76', 'FileSizeLo': 969283854, 'DownloadedSizeMB': 0, 'NZBFilename':
 'How.To.Train.Your.Dragon.2010.iNTERNAL.BDRip.x264-EXViDiNT', 'DupeScore': 7020, 'FinalDir': '', 'FileSizeHi': 0, 'Hist
oryTime': 1476982979, 'DownloadedSizeLo': 0, 'RepairTimeSec': 0, 'UnpackTimeSec': 0, 'ServerStats': [], 'TotalArticles':
 1256, 'NZBNicename': 'How.To.Train.Your.Dragon.2010.iNTERNAL.BDRip.x264-EXViDiNT', 'UrlStatus': 'NONE', 'RemainingFileC
ount': 0, 'ScriptStatus': 'NONE', 'DupeMode': 'ALL', 'ParStatus': 'NONE', 'RetryData': False}, {'NZBName': 'How.To.Train
.Your.Dragon.2010.DVDRip.XviD-TASTE', 'Category': 'Movies', 'DeleteStatus': 'MANUAL', 'Log': [], 'Parameters': [{'Name':
 '*Unpack:', 'Value': 'yes'}], 'MoveStatus': 'NONE', 'UnpackStatus': 'NONE', 'MinPostTime': 1285963998, 'ParTimeSec': 0,
 'Health': 1000, 'PostTotalTimeSec': 0, 'SuccessArticles': 0, 'FileCount': 66, 'ExParStatus': 'NONE', 'Status': 'DELETED
/MANUAL', 'FileSizeMB': 794, 'Deleted': True, 'ExtraParBlocks': 0, 'ID': 75, 'DupeKey': 'tt0892769', 'MaxPostTime': 1285
964050, 'MarkStatus': 'NONE', 'NZBID': 75, 'ScriptStatuses': [], 'CriticalHealth': 894, 'DownloadedSizeHi': 0, 'Kind': '
NZB', 'FailedArticles': 0, 'Name': 'How.To.Train.Your.Dragon.2010.DVDRip.XviD-TASTE', 'MessageCount': 69, 'URL': '', 'Do
wnloadTimeSec': 0, 'DestDir': 'C:\\Users\\Steven\\Downloads\\tmp\\How.To.Train.Your.Dragon.2010.DVDRip.XviD-TASTE.#75',
'FileSizeLo': 832990380, 'DownloadedSizeMB': 0, 'NZBFilename': 'How.To.Train.Your.Dragon.2010.DVDRip.XviD-TASTE', 'DupeS
core': 7010, 'FinalDir': '', 'FileSizeHi': 0, 'HistoryTime': 1476980911, 'DownloadedSizeLo': 0, 'RepairTimeSec': 0, 'Unp
ackTimeSec': 0, 'ServerStats': [], 'TotalArticles': 2174, 'NZBNicename': 'How.To.Train.Your.Dragon.2010.DVDRip.XviD-TAST
E', 'UrlStatus': 'NONE', 'RemainingFileCount': 0, 'ScriptStatus': 'NONE', 'DupeMode': 'ALL', 'ParStatus': 'NONE', 'Retry
Data': False}, {'NZBName': 'How To Train Your Dragon 1 2010 English XviD', 'Category': 'Movies', 'DeleteStatus': 'MANUAL
', 'Log': [], 'Parameters': [{'Name': '*Unpack:', 'Value': 'yes'}], 'MoveStatus': 'NONE', 'UnpackStatus': 'NONE', 'MinPo
stTime': 1436855983, 'ParTimeSec': 0, 'Health': 1000, 'PostTotalTimeSec': 0, 'SuccessArticles': 0, 'FileCount': 59, 'ExP
arStatus': 'NONE', 'Status': 'DELETED/MANUAL', 'FileSizeMB': 797, 'Deleted': True, 'ExtraParBlocks': 0, 'ID': 74, 'DupeK
ey': 'tt0892769', 'MaxPostTime': 1436856500, 'MarkStatus': 'NONE', 'NZBID': 74, 'ScriptStatuses': [], 'CriticalHealth':
898, 'DownloadedSizeHi': 0, 'Kind': 'NZB', 'FailedArticles': 0, 'Name': 'How To Train Your Dragon 1 2010 English XviD',
'MessageCount': 62, 'URL': '', 'DownloadTimeSec': 0, 'DestDir': 'C:\\Users\\Steven\\Downloads\\tmp\\How To Train Your Dr
agon 1 2010 English XviD.#74', 'FileSizeLo': 836005916, 'DownloadedSizeMB': 0, 'NZBFilename': 'How To Train Your Dragon
1 2010 English XviD', 'DupeScore': 7010, 'FinalDir': '', 'FileSizeHi': 0, 'HistoryTime': 1476980911, 'DownloadedSizeLo':
 0, 'RepairTimeSec': 0, 'UnpackTimeSec': 0, 'ServerStats': [], 'TotalArticles': 1275, 'NZBNicename': 'How To Train Your
Dragon 1 2010 English XviD', 'UrlStatus': 'NONE', 'RemainingFileCount': 0, 'ScriptStatus': 'NONE', 'DupeMode': 'ALL', 'P
arStatus': 'NONE', 'RetryData': False}]

'''

sys.exit(POSTPROCESS_NONE)
