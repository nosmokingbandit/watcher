import backup
import datetime
import json
import logging
import os
import shutil
import subprocess
import urllib2
import zipfile

import core
from core.helpers import Url

# get remote hash # git rev-parse origin/master
# get local hash  # git rev-parse HEAD
# Hash history    # git rev-list @{u}

logging = logging.getLogger(__name__)


class Version(object):

    def __init__(self):
        self.install_type = self.get_install_type()

        if self.install_type == u'git':
            self.manager = GitUpdater()
        else:
            self.manager = ZipUpdater()

        return

    # returns 'git' or 'source' depending on install type
    def get_install_type(self):
        if os.path.exists(u'.git'):
            return 'git'
        else:
            return 'source'


class Git(object):
    ''' Class used to execute all GIT commands. '''

    def runner(self, args):
        ''' Runs all git commmands.
        :param args: list of git arguments

        Returns: tuple (output, error message, exit_status).
        '''

        CREATE_NO_WINDOW = 0x08000000

        command = ['git']
        for i in args.split(u' '):
            command.append(i)
        try:
            if os.name == 'nt':
                p = subprocess.Popen(command,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     shell=False,
                                     cwd=core.PROG_PATH,
                                     creationflags=CREATE_NO_WINDOW
                                     )
            else:
                p = subprocess.Popen(command,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     shell=False,
                                     cwd=core.PROG_PATH
                                     )
            output, error = p.communicate()
            exit_status = p.returncode
            return (output.rstrip(), error, exit_status)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'Subprocess:', exc_info=True)
            err = str(e)
            return (err, 'Subprocess error.', 1)

    def get_current_hash(self):
        command = u'rev-parse HEAD'
        output, error, status = self.runner(command)
        return (output, error, status)

    def get_commit_hash_history(self):
        command = u'rev-list @{u}'
        output, error, status = self.runner(command)
        output = output.splitlines()
        return (output, error, status)

    def available(self):
        ''' Checks to see if we can execute git.

        Returns: tuple (output, error message, exit_status).
        '''

        command = u'version'
        output, error, status = self.runner(command)
        output = output.splitlines()
        return (output, error, status)

    def fetch(self):
        ''' Returns: tuple (output, error message, exit_status). '''

        command = u'fetch'
        output, error, status = self.runner(command)
        return (output, error, status)

    def pull(self):
        command = u'pull'
        output, error, status = self.runner(command)
        return (output, error, status)


class GitUpdater(object):

    def __init__(self):
        self.git = Git()

        self.git_available = self.check_git_available()

        if self.git_available[2] == 0:
            self.current_hash = self.git.get_current_hash()
            core.CURRENT_HASH = self.current_hash[0]
        return

    def check_git_available(self):
        git_available = self.git.available()
        if git_available[2] == 1:
            logging.error(u'Could not execute git: {}'.format(git_available[0]))
            return git_available
        else:
            return git_available

    def execute_update(self):
        logging.info(u'Updating from Git.')

        logging.info(u'Cleaning up before updating.')

        for root, dirs, files in os.walk(core.PROG_PATH):
            for file in files:
                if file.endswith(u'.pyc'):
                    os.remove(os.path.join(root, file))

        logging.info(u'Executing git fetch.')
        fetch = self.git.fetch()
        if fetch[2] == 1:
            logging.error(u'Error fetching data from git: {}'.format(fetch[1]))
            return False

        # reset update status so it doesn't ask us to update again
        core.UPDATE_STATUS = None

        logging.info(u'Executing git pull.')
        pull = self.git.pull()

        if pull[2] == 1:
            logging.error(u'Update failed: {}'.format(pull[0]))
            return False
        else:
            logging.info(u'Update successful.')
            return True

    def update_check(self):
        ''' Gets commit delta from GIT.

        Sets core.UPDATE_STATUS to return value.
        Returns dict:
            {'status': 'error', 'error': <error> }
            {'status': 'behind', 'behind_count': #, 'local_hash': 'abcdefg', 'new_hash': 'bcdefgh'}
            {'status': 'current'}
        '''

        logging.info(u'Checking git for a new version.')
        core.UPDATE_LAST_CHECKED = datetime.datetime.now()

        result = {}

        if self.git_available[2] == 1:
            result['status'] = u'error'
            result['error'] = self.git_available[0]
            core.UPDATE_STATUS = result
            return result

        # Make sure our git info is up to date
        fetch = self.git.fetch()
        if fetch[2] == 1:
            logging.error(u'Error fetching data from git: {}'.format(fetch[1]))
            result['status'] = u'error'
            result['error'] = fetch[1]
            core.UPDATE_STATUS = result
            return result

        # check if we got a valid local hash
        if self.current_hash[2] == 1:
            logging.error(u'Error getting local commit hash: {}'.format(self.current_hash[1]))
            result['status'] = u'error'
            result['error'] = self.current_hash[1]
            core.UPDATE_STATUS = result
            return result
        local_hash = self.current_hash[0]
        logging.info(u'Current local hash: {}'.format(local_hash))

        # try to get a history of commit hashes
        commit_history = self.git.get_commit_hash_history()
        if commit_history[2] == 1:
            logging.error(u'Error getting git commit history: {}'.format(commit_history[1]))
            result['status'] = u'error'
            result['error'] = commit_history[1]
            core.UPDATE_STATUS = result
            return result
        commit_list = commit_history[0]

        # make sure our hash is in the history
        if local_hash in commit_list:
            behind_count = commit_list.index(local_hash)
            # if it is the first result we are up to date
            if behind_count == 0:
                result['status'] = u'current'
                core.UPDATE_STATUS = result
                return result
            # if not, find out how far behind we are
            else:
                result['status'] = u'behind'
                result['behind_count'] = behind_count
                result['local_hash'] = local_hash
                result['new_hash'] = commit_list[0]
                core.UPDATE_STATUS = result
                logging.info(u'Update found:')
                logging.info(result)
                return result
        else:
            logging.error(u'Current local hash not in git history.')
            result['status'] = u'error'
            result['error'] = u'Current local hash not in git history.'
            core.UPDATE_STATUS = result
            return result


class ZipUpdater(object):
    ''' Manager for updates install without git.

    Updates by downloading the new zip from github. Moves config,
        database, and posters to temp folder, then extracts zip over
        existing files before restoring config, db, and posters.
    '''

    def __init__(self):
        self.version_file = os.path.join(u'core', u'version')
        self.current_hash = self.get_current_hash()
        core.CURRENT_HASH = self.current_hash
        return

    def get_current_hash(self):
        ''' Gets current commit hash.

        If file watcher/core/version exists, reads hash from file
        If not, gets newest hash from GIT and creates version file

        Sets core.CURRENT_HASH as current commit hash
        '''

        if os.path.isfile(self.version_file):
            with open(self.version_file, 'r') as f:
                hash = f.read()
            return hash
        else:
            hash = self.get_newest_hash()
            if hash:
                with open(self.version_file, 'w') as f:
                    f.write(hash)
        core.CURRENT_HASH = hash
        return hash

    def get_newest_hash(self):
        api_url = u'{}/commits/{}'.format(core.GIT_API, core.CONFIG['Server']['gitbranch'])
        request = Url.request(api_url)
        try:
            response = Url.open(request)
            result = json.loads(response)
            hash = result['sha']
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Could not get newest hash from git.', exc_info=True)
            return None
        return hash

    def update_check(self):
        ''' Gets commit delta from GIT

        Sets core.UPDATE_STATUS to return value.
        Returns dict:
            {'status': 'error', 'error': <error> }
            {'status': 'behind', 'behind_count': #, 'local_hash': 'abcdefg', 'new_hash': 'bcdefgh'}
            {'status': 'current'}
        '''

        os.chdir(core.PROG_PATH)
        logging.info(u'Checking git for a new Zip.')
        core.UPDATE_LAST_CHECKED = datetime.datetime.now()

        result = {}

        logging.info(u'Getting local version hash.')
        local_hash = self.current_hash
        if not local_hash:
            result['status'] = u'error'
            result['error'] = u'Could not get local hash. Check logs for details.'
            core.UPDATE_STATUS = result
            return result

        logging.info(u'Getting newest version hash.')
        newest_hash = self.get_newest_hash()
        if not newest_hash:
            result['status'] = u'error'
            result['error'] = u'Could not get latest update hash. Check logs for details.'
            core.UPDATE_STATUS = result
            return result

        compare_url = u'{}/compare/{}...{}'.format(core.GIT_API, newest_hash, local_hash)

        request = Url.request(compare_url)
        try:
            response = Url.open(request)
            result = json.loads(response)
            behind_count = result['behind_by']
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Could not get update information from git.', exc_info=True)
            result['status'] = u'error'
            result['error'] = u'Could not get update information from git.'
            core.UPDATE_STATUS = result
            return result

        if behind_count == 0:
            result['status'] = u'current'
            core.UPDATE_STATUS = result
            return result
        else:
            result['status'] = u'behind'
            result['behind_count'] = behind_count
            result['local_hash'] = local_hash
            result['new_hash'] = newest_hash
            core.UPDATE_STATUS = result
            return result

    def switch_log(self, new_path=None, handler=None):
        ''' Changes log path to tmp file
        :param new_path: string to new log file     <optional>
        :param handler: object log handler object   <optional>

        One var, and only one var, must be passed.

        Changes the log path the 'new_path/log.txt' or assigns handler

        Used to remove open log file so it can be overwritten
            if neccesay during update.

        Returns object original log handler object
        '''

        import logging.handlers

        if new_path is None and handler is None:
            return False

        if new_path is not None and handler is not None:
            return False

        if new_path:
            formatter = logging.Formatter('%(levelname)s %(asctime)s %(name)s.%(funcName)s: %(message)s')
            new_file = os.path.join(new_path, 'log.txt')
            handler = logging.FileHandler(new_file, 'a')
            handler.setFormatter(formatter)

        log = logging.getLogger()  # root logger
        for hdlr in log.handlers[:]:  # remove all old handlers
            original = hdlr
            hdlr.close()
            log.removeHandler(hdlr)
        log.addHandler(handler)      # set the new handler
        return original

    def execute_update(self):
        os.chdir(core.PROG_PATH)
        update_zip = u'update.zip'
        update_path = u'update'
        new_hash = self.get_newest_hash()

        logging.info(u'Updating from Zip file.')

        logging.info(u'Cleaning up old update files.')
        try:
            if os.path.isfile(update_zip):
                os.remove(update_zip)
            if os.path.isdir(update_path):
                shutil.rmtree(update_path)
            os.mkdir(update_path)
        except Exception, e:
            logging.error(u'Could not delete old update files.', exc_info=True)
            return False

        logging.info(u'Creating temporary update log file.')
        orig_log_handler = self.switch_log(new_path=update_path)

        logging.info(u'Downloading latest Zip.')
        zip_url = u'{}/archive/{}.zip'.format(core.GIT_URL, core.CONFIG['Server']['gitbranch'])
        request = Url.request(zip_url)
        try:
            zip_response = Url.open(request)
            with open(update_zip, 'wb') as f:
                f.write(zip_response)
            del zip_response
        except Exception, e:
            logging.error(u'Could not download latest Zip.', exc_info=True)
            return False

        logging.info(u'Extracting Zip to temporary directory.')
        try:
            with zipfile.ZipFile(update_zip) as f:
                f.extractall(update_path)
        except Exception, e:
            logging.error(u'Could not extract Zip.', exc_info=True)
            return False

        logging.info(u'Backing up user files.')
        backup.backup(require_confirm=False)

        # reset update status so it doesn't ask us to update again
        core.UPDATE_STATUS = None

        logging.info(u'Moving update files.')
        subfolder = u'watcher-{}'.format(core.CONFIG['Server']['gitbranch'])
        update_files_path = os.path.join(update_path, subfolder)
        try:
            files = os.listdir(update_files_path)
            for file in files:
                src = os.path.join(update_files_path, file)
                dst = file

                if os.path.isfile(src):
                    if os.path.isfile(dst):
                        os.remove(dst)
                    shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
        except Exception, e:
            logging.error(u'Could not move update files.', exc_info=True)
            return False

        logging.info(u'Restoring user files.')
        backup.restore(require_confirm=False)

        logging.info(u'Setting new version file.')
        try:
            with open(self.version_file, 'w') as f:
                    f.write(new_hash)
        except Exception, e:
            logging.error(u'Could not update version file.', exc_info=True)
            return False

        logging.info(u'Merging update log with master.')
        with open(orig_log_handler.baseFilename, 'a') as log:
            with open(os.path.join(update_path, 'log.txt'), 'r') as u_log:
                log.write(u_log.read())

        logging.info(u'Changing log handler back to original.')
        self.switch_log(handler=orig_log_handler)

        logging.info(u'Cleaning up temporary files.')
        try:
            shutil.rmtree(update_path)
            os.remove(update_zip)
        except Exception, e: # noqa
            logging.error(u'Could not delete temporary files.', exc_info=True)
            return False

        logging.info(u'Update successful.')
        return True
