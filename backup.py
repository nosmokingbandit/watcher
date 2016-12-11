import argparse
import os
import sys
import shutil
import zipfile

os.chdir(os.path.dirname(os.path.realpath(__file__)))

cwd = os.getcwd()
tmpdir = 'backup_tmp'
# files = 'watcher.sqlite', 'config.cfg'
# paths = '/static/images/posters'
posterpath = os.path.join('static', 'images', 'posters')

print '**############################################################**'
print '**############### Watcher backup/restore tool ################**'
print '** Confirm that Watcher is not running while restoring backup **'
print '**############################################################**'

def backup():
    # check for files and paths
    if not os.path.isfile('watcher.sqlite'):
        if raw_input('Database watcher.sqlite not found. Continue? (y/N): ').lower() != 'y':
            sys.exit(0)
        database = False
    else:
        database = True

    if not os.path.isfile('config.cfg'):
        if raw_input('Config config.cfg not found. Continue? (y/N): ').lower() != 'y':
            sys.exit(0)
        config = False
    else:
        config = True

    if not os.path.isdir(posterpath):
        if raw_input('Config config.cfg not found. Continue? (y/N): ').lower() != 'y':
            sys.exit(0)
        posters = False
    else:
        posters = True

    # make temp dir
    if os.path.isdir(tmpdir):
        print 'Old temporary directory found. Removing.'
        shutil.rmtree(tmpdir)
    print 'Creating temporary backup directory.'
    os.mkdir('backup_tmp')

    if database:
        print 'Copying database.'
        shutil.copy2('watcher.sqlite', tmpdir)

    if config:
        print 'Copying config.'
        shutil.copy2('config.cfg', tmpdir)

    if posters:
        print 'Copying posters.'
        dst = os.path.join(tmpdir, 'posters/')
        os.mkdir(dst)
        for file in os.listdir(posterpath):
            src = os.path.join(posterpath, file)
            shutil.copy2(src, dst)

    # create backup zip
    print 'Creating watcher.zip'
    shutil.make_archive('watcher', 'zip', tmpdir)

    print 'Removing temporary backup directory.'
    shutil.rmtree(tmpdir)

    print '**############################################################**'
    print '**##################### Backup finished ######################**'
    print '**################# Zip backup: watcher.zip ##################**'
    print '**############################################################**'

    sys.exit(0)

def restore():
    if not os.path.isfile('watcher.zip'):
        print 'watcher.zip not found. ' \
        'Place watcher.zip in same directory as backup script.'
        sys.exit(0)

    ans = raw_input('Restoring backup. This will overwrite existing '
                    'database, config, and posters. Continue? (y/N):  ')
    if ans.lower() != 'y':
        sys.exit(0)

    # make temp dir
    if os.path.isdir(tmpdir):
        print 'Old temporary directory found. Removing.'
        shutil.rmtree(tmpdir)
    print 'Creating temporary extraction directory.'
    os.mkdir('backup_tmp')

    print 'Extracting zip.'
    zipf = zipfile.ZipFile('watcher.zip')
    zipf.extractall(tmpdir)

    files = os.listdir(tmpdir)

    if 'watcher.sqlite' in files:
        print 'Restoring database.'
        src = os.path.join(tmpdir, 'watcher.sqlite')
        if os.path.isfile('watcher.sqlite'):
            os.remove('watcher.sqlite')
        shutil.copy(src, cwd)

    if 'config.cfg' in files:
        print 'Restoring config.'
        src = os.path.join(tmpdir, 'config.cfg')
        if os.path.isfile('config.cfg'):
            os.remove('config.cfg')
        shutil.copy(src, cwd)

    if 'posters' in files:
        print 'Restoring posters.'
        tmp_posters = os.path.join(tmpdir, 'posters')
        if not os.path.isdir(tmp_posters):
            print 'Error restoring posters. Not a dir.'
        # remove existing posters folder and contents
        if os.path.isdir(posterpath):
            shutil.rmtree(posterpath)
        # make new poster dir
        os.mkdir(posterpath)

        for poster in os.listdir(tmp_posters):
            src = os.path.join(tmp_posters, poster)
            shutil.copy2(src, posterpath)

    print 'Removing temporary directory.'
    shutil.rmtree(tmpdir)

    print '**############################################################**'
    print '**##################### Backup finished ######################**'
    print '**################# Zip backup: watcher.zip ##################**'
    print '**############################################################**'
    return


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('-b', '--backup', help='Back up to watcher.zip.', action="store_true")
group.add_argument('-r', '--restore', help='Restore from watcher.zip', action="store_true")
args = parser.parse_args()

if args.backup:
    backup()
elif args.restore:
    restore()
else:
    print 'Invalid arguments.'


