# Paths to local things
PROG_PATH = None
CONF_FILE = 'config.cfg'
LOG_DIR = 'logs'
DB_FILE = 'watcher.sqlite'
THEME = 'Default'

# Paths to internet things
GIT_URL = 'https://github.com/nosmokingbandit/watcher'
GIT_REPO = 'https://github.com/nosmokingbandit/watcher.git'
GIT_API = 'https://api.github.com/repos/nosmokingbandit/watcher'

# Server settings
SERVER_ADDRESS = None
SERVER_PORT = None
URL_BASE = ''

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
