# Paths to local things
PROG_PATH = None
CONF_FILE = u'config.cfg'
LOG_DIR = u'logs'
PLUGIN_DIR = u'plugins'
DB_FILE = u'watcher.sqlite'
THEME = u'Default'

# Paths to internet things
GIT_URL = u'https://github.com/nosmokingbandit/watcher'
GIT_REPO = u'https://github.com/nosmokingbandit/watcher.git'
GIT_API = u'https://api.github.com/repos/nosmokingbandit/watcher'

# Server settings
SERVER_ADDRESS = None
SERVER_PORT = None
URL_BASE = u''

# Update info
UPDATE_STATUS = None
UPDATE_LAST_CHECKED = None
UPDATING = False
CURRENT_HASH = None

# Search Scheduler info
NEXT_SEARCH = None

# Store settings after write. Reduces reads from file.
CONFIG = None

# A list of notification data
NOTIFICATIONS = []

# Rate limiting
TMDB_TOKENS = 35
TMDB_LAST_FILL = None

# Global Media Constants
RESOLUTIONS = ['BluRay-4K', 'BluRay-1080P', 'BluRay-720P',
               'WebDL-4K', 'WebDL-1080P', 'WebDL-720P',
               'WebRip-4K', 'WebRip-1080P', 'WebRip-720P',
               'DVD-SD',
               'Screener-1080P', 'Screener-720P',
               'Telesync-SD', 'CAM-SD']
