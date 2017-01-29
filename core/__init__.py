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
