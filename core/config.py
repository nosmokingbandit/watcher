import ConfigParser
import random
import shutil
import os

import logging
logging = logging.getLogger(__name__)

class Config():

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.optionxform = str

        self.file = 'config.cfg'

    def __getitem__(self, h):
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
        try:
            shutil.copy2(self.base_file, self.file)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error('Moving base_config.', exc_info=True)
            raise

        self.config.readfp(open(self.file))

        self.config.set('Search', 'SearchTimeHr', str(random.randint(0, 23)).zfill(2) )
        self.config.set('Search', 'SearchTimeMin', str(random.randint(0, 59)).zfill(2) )

        apikey = "%06x" % random.randint(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        self.config.set('Server', 'apikey', apikey )

        with open(self.file, 'w') as conf_file:
            self.config.write(conf_file)
        return 'Config Saved'

    def write_item(self, category, key, value):

        self.config.readfp(open(self.file))

        self.config.set(category, key, value)

        logging.info('opening file')
        with open(self.file, 'w') as conf_file:
            logging.info('writing file')
            self.config.write(conf_file)

    def write_dict(self, data):
        self.config.read(self.file)

        for cat in data:
            for k, v in data[cat].items():
                if self.config.get(cat, k) != v:
                    self.config.set(cat, k, v)

        with open(self.file, 'w') as cfgfile:
            self.config.write(cfgfile)

    def sections(self):
        self.config.readfp(open(self.file))
        return self.config._sections

    def get_indexers(self):
        ind = self['Indexers']
        indexers = []
        for i in ind:
            if ind[i][2] == 'true':
                indexers.append(ind[i])
        return indexers
