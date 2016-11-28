import subprocess
import core
import os
import datetime
import sys
import urllib2
import json
import shutil
import zipfile

# get remote hash # git rev-parse origin/master
# get local hash  # git rev-parse HEAD
# Hash history    # git rev-list @{u}

import logging
logging = logging.getLogger(__name__)

class Version(object):

    def __init__(self):
        self.install_type = self.get_install_type()

        if self.install_type == 'git':
            self.manager = GitUpdater()
        else:
            self.manager = ZipUpdater()

        return

    # returns 'git' or 'source' depending on install type
    def get_install_type(self):
        git_folder = os.path.join(core.PROG_PATH, '.git')
        if os.path.exists('.git'):
            return 'git'
        else:
            return 'source'


class Git(object):

    # runs git commands, returns tuple (output, error message, exit_status)
    def runner(self, args):
        command = ['git']
        for i in args.split(' '):
            command.append(i)
        try:
            p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=False, cwd=core.PROG_PATH)
            output, error = p.communicate()
            exit_status = p.returncode
            return (output.rstrip(), error, exit_status)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error('Subprocess:', exc_info=True)
            err = str(e)
            return (err, 'Subprocess error.', 1)

    def get_current_hash(self):
        command = 'rev-parse HEAD'
        output, error, status = self.runner(command)
        return (output, error, status)

    def get_commit_hash_history(self):
        command = 'rev-list @{u}'
        output, error, status = self.runner(command)
        output = output.splitlines()
        return (output, error, status)

    def available(self):
        command = 'version'
        output, error, status = self.runner(command)
        output = output.splitlines()
        return (output, error, status)

    def fetch(self):
        command = 'fetch'
        output, error, status = self.runner(command)
        return (output, error, status)

    def pull(self):
        command = 'pull'
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
            logging.info('Could not execute git: {}'.format(git_available[0]))
            return git_available
        else:
            return git_available

    def execute_update(self):
        logging.info('Updating from Git.')

        logging.info('Executing git fetch.')
        fetch = self.git.fetch()
        if fetch[2] == 1:
            logging.error('Error fetching data from git: {}'.format(fetch[1]))
            return False

        # reset update status so it doesn't ask us to update again
        core.UPDATE_STATUS = None

        logging.info('Executing git pull.')
        pull = self.git.pull()

        if pull[2] == 1:
            logging.info('Update failed: {}'.format(pull[0]))
            return False
        else:
            logging.info('Update successful.')
            return True

    def update_check(self):
        '''
        checks if an update is available.
        Sets core.UPDATE_STATUS and returns dict:
        {'status': 'error', 'error': <error> }
        {'status': 'behind', 'behind_count': #, 'local_hash': 'abcdefg', 'new_hash': 'bcdefgh'}
        {'status': 'current'}
        '''
        logging.info('Checking git for a new version.')
        core.UPDATE_LAST_CHECKED = datetime.datetime.now()

        result = {}

        if self.git_available[2] == 1:
            result['status'] = 'error'
            result['error'] = self.git_available[0]
            core.UPDATE_STATUS = result
            return result

        # Make sure our git info is up to date
        fetch = self.git.fetch()
        if fetch[2] == 1:
            logging.error('Error fetching data from git: {}'.format(fetch[1]))
            result['status'] = 'error'
            result['error'] = fetch[1]
            core.UPDATE_STATUS = result
            return result

        # check if we got a valid local hash
        if self.current_hash[2] == 1:
            logging.error('Error getting local commit hash: {}'.format(self.current_hash[1]))
            result['status'] = 'error'
            result['error'] = self.current_hash[1]
            core.UPDATE_STATUS = result
            return result
        local_hash = self.current_hash[0]
        logging.info('Current local hash: {}'.format(local_hash))

        # try to get a history of commit hashes
        commit_history = self.git.get_commit_hash_history()
        if commit_history[2] == 1:
            logging.error('Error getting git commit history: {}'.format(commit_list[1]))
            result['status'] = 'error'
            result['error'] = commit_list[1]
            core.UPDATE_STATUS = result
            return result
        commit_list = commit_history[0]

        # make sure our hash is in the history
        if local_hash in commit_list:
            behind_count = commit_list.index(local_hash)
            # if it is the first result we are up to date
            if behind_count == 0:
                result['status'] = 'current'
                core.UPDATE_STATUS = result
                return result
            # if not, find out how far behind we are
            else:
                result['status'] = 'behind'
                result['behind_count'] = behind_count
                result['local_hash'] = local_hash
                result['new_hash'] = commit_list[0]
                core.UPDATE_STATUS = result
                return result
        else:
            logging.error('Current local hash not in git history.')
            result['status'] = 'error'
            result['error'] = 'Current local hash not in git history.'
            core.UPDATE_STATUS = result
            return result


class ZipUpdater(object):

    def __init__(self):
        self.version_file = os.path.join('core', 'version')
        self.current_hash = self.get_current_hash()
        return

    def get_current_hash(self):
        '''
        If there is a version file in core we read the hash from it.

        If there is no version file then this is the first time Watcher is running. Since we don't know what version a zip from github is we'll just have to assume that it is the newest version for now.

        Sets core.CURRENT_HASH so we can access it everywhere.
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
        api_url = '{}/commits/{}'.format(core.GIT_API, core.GIT_BRANCH)
        request = urllib2.Request( api_url, headers={'User-Agent' : 'Mozilla/5.0'} )
        try:
            response = json.load(urllib2.urlopen( request ) )
            hash = response['sha']
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error('Could not get newest hash from git.', exc_info=True)
            return None
        return hash


    def update_check(self):
        '''
        checks if an update is available.
        Sets core.UPDATE_STATUS and returns dict:
        {'status': 'error', 'error': <error> }
        {'status': 'behind', 'behind_count': #, 'local_hash': 'abcdefg', 'new_hash': 'bcdefgh'}
        {'status': 'current'}
        '''
        os.chdir(core.PROG_PATH)
        logging.info('Checking git for a new Zip.')
        core.UPDATE_LAST_CHECKED = datetime.datetime.now()

        result = {}

        logging.info('Getting local version hash.')
        local_hash = self.current_hash
        if not local_hash:
            result['status'] = 'error'
            result['error'] = 'Could not get local hash. Check logs for details.'
            core.UPDATE_STATUS = result
            return result


        logging.info('Getting newest version hash.')
        newest_hash = self.get_newest_hash()
        if not newest_hash:
            result['status'] = 'error'
            result['error'] = 'Could not get latest update hash. Check logs for details.'
            core.UPDATE_STATUS = result
            return result

        compare_url = '{}/compare/{}...{}'.format(core.GIT_API, newest_hash, local_hash)

        request = urllib2.Request(compare_url, headers={'User-Agent' : 'Mozilla/5.0'} )
        try:
            response = json.load(urllib2.urlopen( request ) )
            behind_count = response['behind_by']
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error('Could not get update information from git.', exc_info=True)
            result['status'] = 'error'
            result['error'] = 'Could not get update information from git.'
            core.UPDATE_STATUS = result
            return result

        if behind_count == 0:
            result['status'] = 'current'
            core.UPDATE_STATUS = result
            return result
        else:
            result['status'] = 'behind'
            result['behind_count'] = behind_count
            result['local_hash'] = local_hash
            result['new_hash'] = newest_hash
            core.UPDATE_STATUS = result
            return result

    def execute_update(self):
        os.chdir(core.PROG_PATH)
        update_zip = 'update.zip'
        update_path = 'update'
        backup_path = os.path.join(update_path, 'backup')
        new_hash = self.get_newest_hash()

        logging.info('Updating from Zip file.')

        logging.info('Cleaning up old update files.')
        try:
            if os.path.isfile(update_zip):
                os.remove(update_zip)
            elif os.path.isdir(update_path):
                shutil.rmtree(update_path)
        except Exception, e:
            logging.error('Could not delete old update files.', exc_info=True)
            return False


        logging.info('Downloading latest Zip.')
        zip_url = '{}/archive/{}.zip'.format(core.GIT_URL, core.GIT_BRANCH )
        request = urllib2.Request(zip_url, headers={'User-Agent' : 'Mozilla/5.0'} )
        try:
            zip_response = urllib2.urlopen(request).read()
            with open(update_zip, 'wb') as f:
                f.write(zip_response)
        except Exception, e:
            logging.error('Could not download latest Zip.', exc_info=True)
            return False

        logging.info('Extracting Zip to temporary directory.')
        try:
            with zipfile.ZipFile(update_zip) as f:
                 f.extractall(update_path)
        except Exception, e:
            logging.error('Could not extract Zip.', exc_info=True)
            return False

        logging.info('Backing up user files.')
        try:
            if os.path.isfile('watcher.sqlite'):
                shutil.copy2('watcher.sqlite', backup_path)
            if os.path.isfile('config.cfg'):
                shutil.copy2('config.cfg', backup_path)
            if os.path.path('logs'):
                shutil.copytree('logs', backup_path)
            posterpath = os.path.join('static', 'images', 'posters')
            if os.path.ispath(posterpath):
                shutil.copytree(posterpath, backup_path)
        except Exception, e:
            logging.error('Could not back up user files.', exc_info=True)
            return False

        # reset update status so it doesn't ask us to update again
        core.UPDATE_STATUS = None

        logging.info('Moving update files.')
        subfolder = 'watcher-{}'.format(core.GIT_BRANCH)
        update_files_path = os.path.join(update_path, subfolder)
        try:
            files = os.listdir(update_files_path)
            for file in files:
                src = os.path.join(update_files_path, file)
                dst = file

                if os.path.isfile(src):
                    os.remove(dst)
                    shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    shutil.rmtree(dst)
                    shutil.copytree(src, dst)
        except Exception, e:
            logging.error('Could not move update files.', exc_info=True)
            return False

        logging.info('Restoring user files.')
        try:
            for file in backup_path:
                src = os.path.join(backup_path, file)
                dst = file

                if os.path.isfile(src):
                    os.remove(dst)
                    shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    shutil.rmtree(dst)
                    shutil.copytree(src, dst)
        except Exception, e:
            logging.error('Could not restore user files.', exc_info=True)
            return False

        logging.info('Setting new version file.')
        try:
            with open(self.version_file, 'w') as f:
                    f.write(new_hash)
        except Exception, e:
            logging.error('Could not update version file.', exc_info=True)
            return False

        logging.info('Cleaning up temporary files.')
        try:
            shutil.rmtree(update_path)
            os.remove(update_zip)
        except Exception, e:
            logging.error('Could not delete temporary files.', exc_info=True)
            return False


        logging.info('Update successful.')
        return True
