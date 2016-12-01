import ConfigParser
import random
import shutil
import os
import core

import logging
logging = logging.getLogger(__name__)

class Config():

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.optionxform = str

        self.file = core.CONF_FILE
        self.base_file = 'core/base_config.cfg'

    def __getitem__(self, h):
        '''
        Replace default <instance>['key'] method.
        Used to get <config>['Section']['key']
        If the value is a list 'one, two, three' it will automatically split it into a list ['one', 'two', 'three'].
        '''
        with open(self.file) as c:
            self.config.readfp(c)
        data = self.config._sections[h]
        if ['__name__'] in data.keys():
            del data['__name__']

        for i in data:
            if ',' in data[i]:
                data[i] = data[i].split(',')
        return data

    def new_config(self):
        '''
        If the config file isn't found this copies base_config to the config directory (watcher/config.cfg default).
        Automatically assigns random values to searchtimehr, searchtimemin, and apikey.
        '''

        try:
            shutil.copy2(self.base_file, self.file)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            print 'Could not move base_config.'
            raise

        self.config.readfp(open(self.file))

        self.config.set('Search', 'searchtimehr', str(random.randint(0, 23)).zfill(2) )
        self.config.set('Search', 'searchtimemin', str(random.randint(0, 59)).zfill(2) )

        apikey = "%06x" % random.randint(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        self.config.set('Server', 'apikey', apikey )

        with open(self.file, 'w') as conf_file:
            self.config.write(conf_file)
        return 'Config Saved'

    def write_item(self, category, key, value):
        '''
        Writes a single item to the config file.
        '''

        self.config.readfp(open(self.file))

        self.config.set(category, key, value)

        logging.info('opening file')
        with open(self.file, 'w') as conf_file:
            logging.info('writing file')
            self.config.write(conf_file)

    def write_dict(self, data):
        '''
        Writes a dict to the config file.
        Data passed should be a dict:
        {'Section': {'key': 'val', 'key2': 'val2'}, 'Section2': {'key': 'val'}}

        '''
        self.config.read(self.file)

        for cat in data:
            self.config.remove_section(cat)
            self.config.add_section(cat)
            for k, v in data[cat].items():
                self.config.set(cat, k, v)

        with open(self.file, 'w') as cfgfile:
            self.config.write(cfgfile)

    def sections(self):
        '''
        Returns a list of sections.
        '''
        self.config.readfp(open(self.file))
        return self.config._sections

    def get_indexers(self):
        '''
        Returns a list of indexers if the indexer is enabled.
        '''
        ind = self['Indexers']
        indexers = []
        for i in ind:
            if ind[i][2] == 'true':
                indexers.append(ind[i])
        return indexers

    def merge_new_options(self):
        '''
        Opens base_config and config, then copies any options that are missing into config.
        '''
        self.config.read([self.base_file, self.file])
        with open(self.file, 'w') as cfgfile:
            self.config.write(cfgfile)
