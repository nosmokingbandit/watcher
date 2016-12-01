from sqlalchemy import *
import os
import json
from core import poster
import sys
import time

import logging
logging = logging.getLogger(__name__)

DB_NAME = 'sqlite:///watcher.sqlite'

class SQL(object):
    '''
    All methods will return False on failure. On success they will return the expected data or True.
    '''

    def __init__(self):
        try:
            self.engine = create_engine(DB_NAME, echo=False, connect_args={'timeout': 30})
            self.metadata = MetaData()
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error('Opening SQL DB.', exc_info=True)
            raise

        self.MOVIES = Table('MOVIES', self.metadata,
                              Column('imdbid', TEXT),
                              Column('title', TEXT),
                              Column('year', TEXT),
                              Column('poster', TEXT),
                              Column('plot', TEXT),
                              Column('tomatourl', TEXT),
                              Column('tomatorating', TEXT),
                              Column('released', TEXT),
                              Column('dvd', TEXT),
                              Column('rated', TEXT),
                              Column('status', TEXT),
                              Column('predb', TEXT),
                              Column('quality', TEXT),
                              Column('finisheddate', TEXT),
                              Column('finishedscore', SMALLINT)
                             )
        self.SEARCHRESULTS = Table('SEARCHRESULTS', self.metadata,
                                     Column('score', SMALLINT),
                                     Column('size', SMALLINT),
                                     Column('category', TEXT),
                                     Column('status', TEXT),
                                     Column('pubdate', TEXT),
                                     Column('title', TEXT),
                                     Column('imdbid', TEXT),
                                     Column('indexer', TEXT),
                                     Column('date_found', TEXT),
                                     Column('info_link', TEXT),
                                     Column('guid', TEXT),
                                     Column('torrentfile', TEXT),
                                     Column('resolution', TEXT),
                                     Column('type', TEXT)
                                    )
        self.MARKEDRESULTS = Table('MARKEDRESULTS', self.metadata,
                                     Column('imdbid', TEXT),
                                     Column('guid', TEXT),
                                     Column('status', TEXT)
                                    )

    def create_database(self):
        logging.info('Creating tables.')
        self.metadata.create_all(self.engine)
        return

    def execute(self, command):
        '''
        We are going to loop this up to 5 times in case the database is locked. After each attempt we wait 1 second to try again. This allows the query that has the database locked to (hopefully) finish. It might (i'm not sure) allow a query to jump in line between a series of queries. So if we are writing search results to every movie at once, the get_user_movies request may be able to jump in between them to get the user's movies to the browser. Maybe.
        '''
        tries = 0
        while tries < 5:
            try:
                if type(command) == list:
                    result = self.engine.execute(*command)
                else:
                    result = self.engine.execute(command)
                return result

            except Exception as e:
                logging.error('SQL Databse Query: {}'.format(command), exc_info=True)
                if 'database is locked' in e.args[0]:
                    logging.info('SQL Query attempt # {}'.format(tries))
                    tries += 1
                    time.sleep(1)
                else:
                    logging.error('SQL Databse Query: {}'.format(command), exc_info=True)
                    raise
        # all tries exhausted
        return False

    def write(self, TABLE, DB_STRING):
        '''
        Takes dict DB_STRING and writes to TABLE.
        DB_STRING must have key:val matching Column:Value in table.
        Returns Bool on success.
        '''
        logging.info('Writing data to {}'.format(TABLE))

        cols = ', '.join(DB_STRING.keys())
        vals = DB_STRING.values()

        qmarks = ', '.join(['?'] * len(DB_STRING))

        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (TABLE, cols, qmarks)

        command = [sql, vals]

        if self.execute(command):
            return True
        else:
            logging.error('EXECUTE SQL.WRITE FAILED.')
            return False

    def write_search_results(self, LIST):
        '''
        Takes list of dicts to write into SEARCHRESULTS.
        '''

        logging.info('Writing batch into SEARCHRESULTS')

        INSERT = self.SEARCHRESULTS.insert()

        command = [INSERT, LIST]

        if self.execute(command):
            return True
        else:
            logging.error('EXECUTE SQL.WRITE_SEARCH_RESULTS FAILED.')
            return False

    def update(self, TABLE, COLUMN, VALUE, imdbid='', guid=''):
        '''
        Updates single value in existing table row.
        Selects row to update from imdbid or guid.
        Sets COLUMN to VALUE.
        Returns Bool.
        '''

        if imdbid:
            idcol = 'imdbid'
            idval = imdbid
        elif guid:
            idcol = 'guid'
            idval = guid
        else:
            return 'ID ERROR'

        logging.info('Updating {} to {} in {}.'.format(idval, VALUE, TABLE))

        sql = 'UPDATE {} SET {}=? WHERE {}=?'.format(TABLE, COLUMN, idcol)
        vals = (VALUE, idval)

        command = [sql, vals]

        if self.execute(command):
            return True
        else:
            logging.error('EXECUTE SQL.UPDATE FAILED.')
            return False

    def get_user_movies(self):
        '''
        Returns list of dicts with all information in MOVIES
        '''

        logging.info('Retreving list of user\'s movies.')
        TABLE = 'MOVIES'

        command = 'SELECT * FROM {} ORDER BY title ASC'.format(TABLE)

        result = self.execute(command)

        if result:
            return result.fetchall()
        else:
            logging.error('EXECUTE SQL.GET_USER_MOVIES FAILED.')
            return False

    def get_movie_details(self, imdbid):
        '''
        Returns dict of single movie details from MOVIES.
        Selects by imdbid.
        '''

        logging.info('Retreving details for {}.'.format(imdbid))

        command = 'SELECT * FROM MOVIES WHERE imdbid="{}"'.format(imdbid)

        result = self.execute(command)

        if result:
            return result.fetchone()
        else:
            return False

    def get_search_results(self, imdbid):
        '''
        Returns list of dicts for all SEARCHRESULTS that match imdbid
        '''

        logging.info('Retreving Search Results for {}.'.format(imdbid))
        TABLE = 'SEARCHRESULTS'

        command ='SELECT * FROM {} WHERE imdbid="{}" ORDER BY score DESC, size DESC'.format(TABLE, imdbid)

        results = self.execute(command)

        if results:
            return results.fetchall()
        else:
            return False

    def get_marked_results(self, imdbid):
        '''
        Returns dict of MARKEDRESULTS
        {guid:status, guid:status, etc}
        '''
        logging.info('Retreving Marked Results for {}.'.format(imdbid))

        TABLE = 'MARKEDRESULTS'

        results = {}

        command ='SELECT * FROM {} WHERE imdbid="{}"'.format(TABLE, imdbid)

        data = self.execute(command)

        if data:
            for i in data.fetchall():
                results[i['guid']] = i['status']
            return results
        else:
            return False

    def remove_movie(self, imdbid):
        '''
        Doesn't access sql directly, but instructs other methods to delete all information that matches imdbid.
        Removes from MOVIE, SEARCHRESULTS, and deletes poster.
        Keeps MARKEDRESULTS.
        '''
        logging.info('Removing {} from {}.'.format(imdbid, 'MOVIES'))

        if not self.delete('MOVIES', 'imdbid', imdbid):
            return False

        logging.info('Removing any stored search results for {}.'.format(imdbid))

        if self.row_exists('SEARCHRESULTS', imdbid):
            if not self.purge_search_results(imdbid=imdbid):
                return False

        logging.info('{} removed.'.format(imdbid))
        return True

    def delete(self, TABLE, idcol, idval):
        '''
        Deletes row where idcol == idval
        Returns Bool.
        '''

        logging.info('Removing from {} where {} is {}.'.format(TABLE, idcol, idval))

        command = 'DELETE FROM {} WHERE {}="{}"'.format(TABLE, idcol, idval)

        if self.execute(command):
            return True
        else:
            return False

    def purge_search_results(self, imdbid=''):
        '''
        Be careful with this one. Supplying an imdbid deletes search results for that movie. If you do not supply an imdbid it purges FOR ALL MOVIES.

        BE CAREFUL.
        '''
        TABLE = 'SEARCHRESULTS'

        if imdbid:
            command = 'DELETE FROM {} WHERE imdbid="{}"'.format(TABLE, imdbid)
        else:
            command = 'DELETE FROM {}'.format(TABLE)

        if self.execute(command):
            return True
        else:
            return False

    def get_distinct(self, TABLE, column, idcol, idval):
        '''
        Returns list of dictinct values from TABLE where idcol == idval.
        ['val1', 'val2', 'val3']
        '''

        logging.info('Getting distinct values for {} in {}'.format(idval, TABLE))

        command = 'SELECT DISTINCT {} FROM {} WHERE {}="{}"'.format(column, TABLE, idcol, idval)

        data = self.execute(command)

        if data:
            l = []
            for i in data.fetchall():
                l.append(i[column])
            return l
        else:
            logging.error('EXECUTE SQL.GET_DISTINCT FAILED.')
            return False

    def row_exists(self, TABLE, imdbid='', guid=''):
        '''
        Checks TABLE for imdbid or guid.
        Returns Bool if found.

        Used to determine if we need to add a row or update existing row.
        '''

        if imdbid:
            idcol = 'imdbid'
            idval = imdbid
        elif guid:
            idcol = 'guid'
            idval = guid
        else:
            return 'ID ERROR'

        command = 'SELECT 1 FROM {} WHERE {}="{}"'.format(TABLE, idcol, idval)

        row = self.execute(command)

        if row == False or row.fetchone() == None:
            return False
        else:
        # this will return True if there was a sql error to prevent accidental double-entires. Probably not the best solution, but it works.
            return True

    def get_single_search_result(self, guid):
        '''
        Returns dict from SEARCHRESULTS for single row.
        '''

        logging.info('Retreving search result details for {}.'.format(guid))

        command = 'SELECT * FROM SEARCHRESULTS WHERE guid="{}"'.format(guid)

        result = self.execute(command)

        if result:
            return result.fetchone()
        else:
            return False

    def get_imdbid_from_guid(self, guid):
        '''
        Mainly used for post-processing.

        Takes guid and looks in SEARCHRESULTS for matching row.
        If found, returns string imdbid.
        '''

        logging.info('Retreving imdbid for {}.'.format(guid))

        command = 'SELECT imdbid FROM SEARCHRESULTS WHERE guid="{}"'.format(guid)

        imdbid = self.execute(command)

        if imdbid:
            return imdbid.fetchone()[0]
        else:
            return False

    '''
    TAG REMOVE
    These next methods are for adding columns to tables. It will run at program start.

    _get_existing_columns gathers a dict of existing tables and columns:
    {'TABLENAME': ['col1', 'col2', 'col3'], 'TABLENAME2': ['col1', 'col2', 'col3']}

    _get_intended_schema gets a dict of tables, columns, and types that we want to have in the table:

    {'TABLENAME': {'col1': 'TEXT', 'col2': 'SMALLINT', 'col3': 'TEXT'},'TABLENAME2': {'col1': 'TEXT', 'col2': 'SMALLINT', 'col3': 'TEXT'}}

    Then we find what is in 'intended' that *isnt* in existing and add it.

    This should be removed before going public. This is just for adding to the table schema on the fly while testing and adding features.

    '''

    def _get_existing_columns(self):
        table_dict = {}

        # get list of tables in db:
        command = 'SELECT name FROM sqlite_master WHERE type="table"'
        tables = self.execute(command)

        if not tables:
            return False

        for i in tables:
            i = i[0]
            command = 'PRAGMA table_info({})'.format(i)
            columns = self.execute(command)
            if not columns:
                return False
            l = []
            for col in columns:
                l.append(col['name'])
            table_dict[i] = l

        return table_dict

    def _get_intended_schema(self):
        d = {}
        for table in self.metadata.tables.keys():
            selftable = getattr(self, table)
            d2 = {}
            for i in selftable.c:
                d2[i.name] = str(i.type)
            d[table] = d2
        return d

    def add_new_columns(self):
        existing = self._get_existing_columns()
        intended = self._get_intended_schema()

        if not existing or not intended:
            raise ValueError('Could not parse database schema.')

        tables = existing.keys()

        for TABLE in tables:
            existing_columns = existing[TABLE]
            intended_columns = intended[TABLE]
            for i in intended_columns:
                if i not in existing_columns:
                    command = 'ALTER TABLE {} ADD COLUMN {} {}'.format(TABLE, i, intended_columns[i])
                    if not self.execute(command):
                        raise ValueError('Could not alter database. {}'.format(command))
        return
