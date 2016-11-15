#--import sqlite3
from sqlalchemy import *
import os
import json
from core import poster
import sys

import logging
logging = logging.getLogger(__name__)

DB_NAME = 'sqlite:///watcher.sqlite'
class SQL(object):

    def __init__(self):
        try:
            self.engine = create_engine(DB_NAME)
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
                            Column('predb', TEXT)
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
                                   Column('resolution', TEXT),
                                   Column('type', TEXT),
                                   Column('downloader_id', TEXT)
                                  )

        self.MARKEDRESULTS = Table('MARKEDRESULTS', self.metadata,
                                   Column('imdbid', TEXT),
                                   Column('guid', TEXT),
                                   Column('status', TEXT)
                                  )


    def create_database(self):
        logging.info('Creating tables.')
        self.metadata.create_all(self.engine)

    # accepts str TABLE and dict DB_STRING to be written
    def write(self, TABLE, DB_STRING):

        logging.info('Writing data to {}'.format(TABLE))
        if TABLE == 'MOVIES':
            insert = self.MOVIES.insert()
        if TABLE == 'SEARCHRESULTS':
            insert = self.SEARCHRESULTS.insert()
        if TABLE == 'MARKEDRESULTS':
            insert = self.MARKEDRESULTS.insert()

        # this is super slow and i don't know what to do about it.
        self.engine.execute(insert, DB_STRING)
        return 'success'

    def write_search_results(self, LIST):
        TABLE = 'SEARCHRESULTS'
        logging.info('Writing batch into table {}'.format(TABLE))

        self.engine.execute(self.SEARCHRESULTS.insert(), LIST)
        return 'success'

    def update(self, TABLE, COLUMN, VALUE, imdbid='', guid=''):
        if imdbid:
            idcolumn = 'imdbid'
            idval = imdbid
        elif guid:
            idcolumn = 'guid'
            idval = guid

        command = 'UPDATE {} SET {}="{}" WHERE {}="{}"'.format(TABLE, COLUMN, VALUE, idcolumn, idval)

        self.engine.execute(command)

    def get_user_movies(self):

        logging.info('Retreving list of user\'s movies.')
        TABLE = 'MOVIES'

        command = 'SELECT * FROM {} ORDER BY title ASC'.format(TABLE)

        movies = self.engine.execute(command).fetchall()

        return movies

    def get_movie_details(self, imdbid):
        logging.info('Retreving details for {}.'.format(imdbid))
        command = 'SELECT * FROM MOVIES WHERE imdbid="{}"'.format(imdbid)
        details = self.engine.execute(command).fetchone()
        return details

    def get_search_results(self, imdbid):
        TABLE = 'SEARCHRESULTS'
        logging.info('Retreving Search Results for {}.'.format(imdbid))
        command ='SELECT * FROM {} WHERE imdbid="{}" ORDER BY score DESC, size DESC'.format(TABLE, imdbid)

        return self.engine.execute(command).fetchall()

        if results:
            return results
        else:
            return None

    # returns a dict {guid:status, etc}
    def get_marked_results(self, imdbid):
        results = {}
        TABLE = 'MARKEDRESULTS'
        logging.info('Retreving Marked Results for {}.'.format(imdbid))
        command ='SELECT * FROM {} WHERE imdbid="{}"'.format(TABLE, imdbid)
        data = self.engine.execute(command).fetchall()

        for i in data:
            results[i['guid']] = i['status']

        return results

    def remove_movie(self, imdbid):
        TABLE = 'MOVIES'

        logging.info('Removing {} from {}.'.format(imdbid, TABLE))
        self.delete(TABLE, 'imdbid', imdbid)

        logging.info('Removing any stored search results for {}.'.format(imdbid))
        TABLE = 'SEARCHRESULTS'
        if self.row_exists(TABLE, imdbid):
            self.delete(TABLE, 'imdbid', imdbid)

        logging.info('{} removed.'.format(imdbid))

    def delete(self, TABLE, id_col, id_val):
        logging.info('Removing from {} where {} is {}.'.format(TABLE, id_col, id_val))
        command = 'DELETE FROM {} WHERE {}="{}"'.format(TABLE, id_col, id_val)
        self.engine.execute(command)

    def purge_search_results(self, imdbid=''):
        TABLE = 'SEARCHRESULTS'

        if imdbid:
            command = 'DELETE * FROM {} WHERE imdbid="{}"'.format(TABLE, imdbid)
        else:
            command = 'DELETE FROM {}'.format(TABLE)

        self.engine.execute(command)

    def get_distinct(self, TABLE, column, id_col, id_val):
        command = 'SELECT DISTINCT {} FROM {} WHERE {}="{}"'.format(column, TABLE, id_col, id_val)
        data = self.engine.execute(command).fetchall()

        l = []
        for i in data:
            l.append(i[column])
        return l

    # returns bool if item exists in table. Used to check if we need to write new or update existing row.
    def row_exists(self, TABLE, imdbid='', guid=''):
        if imdbid:
            column = 'imdbid'
            id = imdbid
        elif guid:
            column = 'guid'
            id = guid
        else:
            return 'ID ERROR'

        logging.info('Checking if {}:{} already exists in {}.'.format(column, id, TABLE))
        command = 'SELECT count(*) FROM {} WHERE {}="{}"'.format(TABLE, column, id)

        count = self.engine.execute(command).fetchone()

        if count['count(*)'] == 0:
            logging.info('Table {} does not contain {}:{}.'.format(TABLE, column, id))
            return False
        if count['count(*)'] != 0:
            logging.info('Table {} contains {}:{}.'.format(TABLE, column, id))
            return True

    def get_single_search_result(self, guid):
        logging.info('Retreving search result details for {}.'.format(guid))
        command = 'SELECT * FROM SEARCHRESULTS WHERE guid="{}"'.format(guid)
        details = self.engine.execute(command).fetchone()

        return details

    def get_imdbid_from_guid(self, guid):
        logging.info('Retreving imdbid for {}.'.format(guid))
        command = 'SELECT imdbid FROM SEARCHRESULTS WHERE guid="{}"'.format(guid)
        imdbid = self.engine.execute(command).fetchone()

        if imdbid:
            return imdbid[0]
        else:
            return None
