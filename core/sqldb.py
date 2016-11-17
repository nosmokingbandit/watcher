#--import sqlite3
from sqlalchemy import Table, Column, Integer, String, DateTime, Text, ForeignKey, create_engine, bindparam, column
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import json
from core import poster
import sys

import logging
logging = logging.getLogger(__name__)

DB_NAME = 'sqlite:///watcher.sqlite'
Base = declarative_base()
class SQL(object):

    def __init__(self):
        try:
            self.engine = create_engine(DB_NAME, connect_args={'timeout': 15})
            self.session = sessionmaker(bind = self.engine)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error('Opening SQL DB.', exc_info=True)
            raise


    def create_database(self):
        logging.info('Creating tables.')
        Base.metadata.create_all(self.engine)

    # accepts str TABLE and dict DB_STRING to be written
    def write(self, TABLE, DB_STRING):
        logging.info('Writing data to {}'.format(TABLE))

        TABLE = self.tablename(TABLE)

        sess = self.session()
        sess.add(TABLE(**DB_STRING))
        sess.commit()
        sess.close()

        # this can be super slow and i don't know what to do about it.
        return 'success'

    def write_search_results(self, LIST):
        logging.info('Writing batch into SEARCHRESULTS')

        sess = self.session()

        for i in LIST:
            sess.add(SEARCHRESULTS(**i))

        sess.commit()
        sess.close()

        return 'success'

    def update(self, TABLE, COLUMN, VALUE, imdbid='', guid=''):

        TABLE = self.tablename(TABLE)
        sess = self.session()

        if imdbid:

            idcol = getattr(TABLE, 'imdbid')
            idval = imdbid
        elif guid:

            idcol = getattr(TABLE, 'guid')
            idval = guid
        else:
            sess.close()
            return 'ID ERROR'

        logging.info('Updating {} to {}'.format(idcol, VALUE))
        sess.query(TABLE).filter(idcol==idval).update({COLUMN: VALUE})

        sess.commit()
        sess.close()

    # Returns a list of dicts with all movie information
    def get_user_movies(self):

        logging.info('Retreving list of user\'s movies.')
        TABLE = self.tablename('MOVIES')
        sess = self.session()

        data = sess.query(TABLE).order_by(TABLE.title.asc()).all()
        sess.close()
        movies = []
        for i in data:
            movies.append(i.__dict__)

        return movies

    # Returns dict of a single movie's information
    def get_movie_details(self, imdbid):
        logging.info('Retreving details for {}.'.format(imdbid))
        TABLE = self.tablename('MOVIES')
        sess = self.session()

        command = 'SELECT * FROM MOVIES WHERE imdbid="{}"'.format(imdbid)

        data = sess.query(TABLE).filter(TABLE.imdbid==imdbid).first()
        sess.close()
        return data.__dict__

    def get_search_results(self, imdbid):
        logging.info('Retreving Search Results for {}.'.format(imdbid))
        TABLE = self.tablename('SEARCHRESULTS')
        sess = self.session()


        command ='SELECT * FROM {} WHERE imdbid="{}" ORDER BY score DESC, size DESC'.format(TABLE, imdbid)

        data = sess.query(TABLE).filter(TABLE.imdbid==imdbid).order_by(TABLE.score.desc()).order_by(TABLE.size.desc()).all()
        sess.close()
        l = []
        for i in data:
            l.append(i.__dict__)
        return l

    # returns a dict {guid:status, guid:status, etc}
    def get_marked_results(self, imdbid):
        logging.info('Retreving Marked Results for {}.'.format(imdbid))

        TABLE = self.tablename('MARKEDRESULTS')
        sess = self.session()

        data = sess.query(TABLE).filter(TABLE.imdbid==imdbid).all()
        sess.close()

        results = {}
        for i in data:
            results[i.__dict__['guid']] = i.__dict__['status']

        return results

    def remove_movie(self, imdbid):
        logging.info('Removing {} from {}.'.format(imdbid, 'MOVIES'))
        self.delete('MOVIES', 'imdbid', imdbid)

        logging.info('Removing any stored search results for {}.'.format(imdbid))

        TABLE = 'SEARCHRESULTS'
        if self.row_exists(TABLE, imdbid):
            self.purge_search_results(imdbid=imdbid)

        logging.info('{} removed.'.format(imdbid))

    def delete(self, TABLE, id_col, id_val):
        logging.info('Removing from {} where {} is {}.'.format(TABLE, id_col, id_val))

        TABLE = self.tablename(TABLE)
        sess = self.session()

        id_col = getattr(TABLE, id_col)

        sess.query(TABLE).filter(id_col==id_val).delete()

        sess.commit()
        sess.close()

    def purge_search_results(self, imdbid=''):
        TABLE = self.tablename('SEARCHRESULTS')
        sess = self.session()

        if imdbid:
            sess.query(TABLE).filter(TABLE.imdbid==imdbid).delete()
        else:
            sess.query(TABLE).delete()

        sess.commit()
        sess.close()


    # returns a list of distinct values ['val1', 'val2', 'val3']
    def get_distinct(self, TABLE, column, id_col, id_val):

        TABLE = self.tablename(TABLE)
        sess = self.session()

        id_col = getattr(TABLE, id_col)
        table_col = getattr(TABLE, column)

        data = sess.query(table_col).filter(id_col==id_val).distinct().all()

        sess.close()

        l = []
        for i in data:
            l.append(i[0])
        return l

    # returns bool if item exists in table. Used to check if we need to write new or update existing row.
    def row_exists(self, TABLE, imdbid='', guid=''):
        logging.info('Checking if {} already exists in {}.'.format(id, TABLE))

        TABLE = self.tablename(TABLE)
        sess = self.session()

        if imdbid:
            logging.info('Checking if {} already exists in {}.'.format(imdbid, TABLE))
            idcol = getattr(TABLE, 'imdbid')
            idval = imdbid
        elif guid:
            logging.info('Checking if {} already exists in {}.'.format(guid, TABLE))
            idcol = getattr(TABLE, 'guid')
            idval = guid
        else:
            sess.close()
            return 'ID ERROR'

        row = sess.query(TABLE).filter(idcol==idval).all()

        sess.close()

        if row:
            return True
        else:
            return False



    def get_single_search_result(self, guid):
        logging.info('Retreving search result details for {}.'.format(guid))

        TABLE = self.tablename('SEARCHRESULTS')
        sess = self.session()

        result = sess.query(TABLE).filter(TABLE.guid==guid).first()
        sess.close()

        return result.__dict__

    def get_imdbid_from_guid(self, guid):
        logging.info('Retreving imdbid for {}.'.format(guid))

        TABLE = self.tablename('SEARCHRESULTS')
        sess = self.session()

        data = sess.query(TABLE).filter(TABLE.guid==guid).first().__dict__

        sess.close()
        return data['imdbid']

    # takes passed string and returns corresponding table object
    def tablename(self, TABLE):
        for c in Base._decl_class_registry.values():
            if hasattr(c, '__tablename__') and c.__tablename__ == TABLE:
                return c



class MOVIES(Base):

    __tablename__ = 'MOVIES'

    imdbid = Column(Text, primary_key=True)
    title = Column(Text)
    year = Column(Text)
    poster = Column(Text)
    plot = Column(Text)
    tomatourl = Column(Text)
    tomatorating = Column(Text)
    released = Column(Text)
    dvd = Column(Text)
    rated = Column(Text)
    status = Column(Text)
    predb = Column(Text)

class SEARCHRESULTS(Base):

    __tablename__ = 'SEARCHRESULTS'

    score = Column(Integer)
    size = Column(Integer)
    category = Column(Text)
    status = Column(Text)
    pubdate = Column(Text)
    title = Column(Text)
    imdbid = Column(Text)
    indexer = Column(Text)
    date_found = Column(Text)
    info_link = Column(Text)
    guid = Column(Text, primary_key=True)
    resolution = Column(Text)
    type = Column(Text)

class MARKEDRESULTS(Base):

    __tablename__ = 'MARKEDRESULTS'

    imdbid = Column(Text)
    guid = Column(Text, primary_key=True)
    status = Column(Text)


