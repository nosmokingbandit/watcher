import core
import logging
import time
import json

from sqlalchemy import *

logging = logging.getLogger(__name__)


class SQL(object):
    '''
    All methods will return False on failure.
    On success they will return the expected data or True.
    '''

    def __init__(self):
        DB_NAME = u'sqlite:///{}'.format(core.DB_FILE)
        try:
            self.engine = create_engine(DB_NAME, echo=False, connect_args={'timeout': 30})
            self.metadata = MetaData()
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Opening SQL DB.', exc_info=True)
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
                                   Column('type', TEXT),
                                   Column('downloadid', TEXT)
                                   )
        self.MARKEDRESULTS = Table('MARKEDRESULTS', self.metadata,
                                   Column('imdbid', TEXT),
                                   Column('guid', TEXT),
                                   Column('status', TEXT)
                                   )

    def create_database(self):
        logging.info(u'Creating tables.')
        self.metadata.create_all(self.engine)
        return

    def execute(self, command):
        '''
        We are going to loop this up to 5 times in case the database is locked.
        After each attempt we wait 1 second to try again. This allows the query
            that has the database locked to (hopefully) finish. It might
            (i'm not sure) allow a query to jump in line between a series of
            queries. So if we are writing searchresults to every movie at once,
            the get_user_movies request may be able to jump in between them to
            get the user's movies to the browser. Maybe.
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
                logging.error(u'SQL Databse Query: {}'.format(command), exc_info=True)
                if 'database is locked' in e.args[0]:
                    logging.info(u'SQL Query attempt # {}'.format(tries))
                    tries += 1
                    time.sleep(1)
                else:
                    logging.error(u'SQL Databse Query: {}'.format(command), exc_info=True)
                    raise
        # all tries exhausted
        return False

    def write(self, TABLE, DB_STRING):
        '''
        Takes dict DB_STRING and writes to TABLE.
        DB_STRING must have key:val matching Column:Value in table.
        Returns Bool on success.
        '''

        logging.info(u'Writing data to {}'.format(TABLE))

        cols = u', '.join(DB_STRING.keys())
        vals = DB_STRING.values()

        qmarks = u', '.join(['?'] * len(DB_STRING))

        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (TABLE, cols, qmarks)

        command = [sql, vals]

        if self.execute(command):
            return True
        else:
            logging.error(u'EXECUTE SQL.WRITE FAILED.')
            return False

    def write_search_results(self, LIST):
        '''
        Takes list of dicts to write into SEARCHRESULTS.
        '''

        logging.info(u'Writing batch into SEARCHRESULTS')

        INSERT = self.SEARCHRESULTS.insert()

        command = [INSERT, LIST]

        if self.execute(command):
            return True
        else:
            logging.error(u'EXECUTE SQL.WRITE_SEARCH_RESULTS FAILED.')
            return False

    def update(self, TABLE, COLUMN, VALUE, imdbid='', guid=''):
        '''
        Updates single value in existing table row.
        Selects row to update from imdbid or guid.
        Sets COLUMN to VALUE.
        Returns Bool.
        '''

        if imdbid:
            idcol = u'imdbid'
            idval = imdbid
        elif guid:
            idcol = u'guid'
            idval = guid
        else:
            return 'ID ERROR'

        logging.info(u'Updating {} to {} in {}.'.format(idval, VALUE, TABLE))

        sql = u'UPDATE {} SET {}=? WHERE {}=?'.format(TABLE, COLUMN, idcol)
        vals = (VALUE, idval)

        command = [sql, vals]

        if self.execute(command):
            return True
        else:
            logging.error(u'EXECUTE SQL.UPDATE FAILED.')
            return False

    def get_user_movies(self):
        ''' Gets all info in MOVIES

        Returns list of dicts with all information in MOVIES
        '''

        logging.info(u'Retreving list of user\'s movies.')
        TABLE = u'MOVIES'

        command = u'SELECT * FROM {} ORDER BY title ASC'.format(TABLE)

        result = self.execute(command)

        if result:
            lst = []
            for i in result:
                i = dict(i)
                i['quality'] = json.loads(i['quality'])
                lst.append(i)
            return lst
        else:
            logging.error(u'EXECUTE SQL.GET_USER_MOVIES FAILED.')
            return False

    def get_movie_details(self, idcol, idval):
        ''' Returns dict of single movie details from MOVIES.
        :param idcol: str identifying column
        :param idval: str identifying value

        Looks through MOVIES for idcol:idval

        Returns dict of first match
        '''

        logging.info(u'Retreving details for {}.'.format(idval))

        command = u'SELECT * FROM MOVIES WHERE {}="{}"'.format(idcol, idval)

        result = self.execute(command)

        if result:
            data = result.fetchone()
            return dict(data)
        else:
            return False

    def get_search_results(self, imdbid):
        ''' Gets all search results for a given movie
        :param imdbid: str imdb id #

        Returns list of dicts for all SEARCHRESULTS that match imdbid
        '''

        logging.info(u'Retreving Search Results for {}.'.format(imdbid))
        TABLE = u'SEARCHRESULTS'

        command = u'SELECT * FROM {} WHERE imdbid="{}" ORDER BY score DESC, size DESC'.format(TABLE, imdbid)

        results = self.execute(command)

        if results:
            return results.fetchall()
        else:
            return False

    def get_marked_results(self, imdbid):
        ''' Gets all entries in MARKEDRESULTS for given movie
        :param imdbid: str imdb id #

        Returns dict {guid:status, guid:status, etc}
        '''

        logging.info(u'Retreving Marked Results for {}.'.format(imdbid))

        TABLE = u'MARKEDRESULTS'

        results = {}

        command = u'SELECT * FROM {} WHERE imdbid="{}"'.format(TABLE, imdbid)

        data = self.execute(command)

        if data:
            for i in data.fetchall():
                results[i['guid']] = i['status']
            return results
        else:
            return False

    def remove_movie(self, imdbid):
        ''' Removes movie and search results from DB
        :param imdbid: str imdb id #

        Doesn't access sql directly, but instructs other methods to delete all information that matches imdbid.

        Removes from MOVIE, SEARCHRESULTS, and deletes poster. Keeps MARKEDRESULTS.

        Returns True/False on success/fail or None if movie doesn't exist in DB.
        '''

        logging.info(u'Removing {} from {}.'.format(imdbid, 'MOVIES'))

        if not self.row_exists('MOVIES', imdbid=imdbid):
            return None

        if not self.delete('MOVIES', 'imdbid', imdbid):
            return False

        logging.info(u'Removing any stored search results for {}.'.format(imdbid))

        if self.row_exists('SEARCHRESULTS', imdbid):
            if not self.purge_search_results(imdbid=imdbid):
                return False

        logging.info(u'{} removed.'.format(imdbid))
        return True

    def delete(self, TABLE, idcol, idval):
        ''' Deletes row where idcol == idval
        :param idcol: str identifying column
        :param idval: str identifying value

        Returns Bool.
        '''

        logging.info(u'Removing from {} where {} is {}.'.format(TABLE, idcol, idval))

        command = u'DELETE FROM {} WHERE {}="{}"'.format(TABLE, idcol, idval)

        if self.execute(command):
            return True
        else:
            return False

    def purge_search_results(self, imdbid=''):
        ''' Deletes all search results
        :param imdbid: str imdb id # <optional>

        Be careful with this one. Supplying an imdbid deletes search results for that
            movie. If you do not supply an imdbid it purges FOR ALL MOVIES.

        BE CAREFUL.

        Returns Bool
        '''

        TABLE = u'SEARCHRESULTS'

        if imdbid:
            command = u'DELETE FROM {} WHERE imdbid="{}"'.format(TABLE, imdbid)
        else:
            command = u'DELETE FROM {}'.format(TABLE)

        if self.execute(command):
            return True
        else:
            return False

    def get_distinct(self, TABLE, column, idcol, idval):
        ''' Gets unique values in TABLE
        :param TABLE: str table name
        :param column: str column to return
        :param idcol: str identifying column
        :param idval: str identifying value

        Gets values in TABLE:column where idcol == idval

        Returns list ['val1', 'val2', 'val3']
        '''

        logging.info(u'Getting distinct values for {} in {}'.format(idval, TABLE))

        command = u'SELECT DISTINCT {} FROM {} WHERE {}="{}"'.format(column, TABLE, idcol, idval)

        data = self.execute(command)

        if data:
            data = data.fetchall()

            if len(data) == 0:
                return None

            lst = []
            for i in data:
                lst.append(i[column])
            return lst
        else:
            logging.error(u'EXECUTE SQL.GET_DISTINCT FAILED.')
            return False

    def row_exists(self, TABLE, imdbid='', guid='', downloadid=''):
        ''' Checks if row exists in table
        :param TABLE: str name of sql table to look through
        :param imdbid: str imdb identification number <optional>
        :param guid: str download guid <optional>
        :param downloadid: str downloader id <optional>

        Checks TABLE for imdbid, guid, or downloadid.
        Exactly one optional variable must be supplied.

        Used to check if we need to add row or update existing row.

        Returns Bool of found status
        '''

        if imdbid:
            idcol = u'imdbid'
            idval = imdbid
        elif guid:
            idcol = u'guid'
            idval = guid
        elif downloadid:
            idcol = u'downloadid'
            idval = downloadid

        else:
            return 'ID ERROR'

        command = u'SELECT 1 FROM {} WHERE {}="{}"'.format(TABLE, idcol, idval)

        row = self.execute(command)

        if row is False or row.fetchone() is None:
            return False
        else:
            return True

    def get_single_search_result(self, idcol, idval):
        ''' Gets single search result
        :param idcol: str identifying column
        :param idval: str identifying value

        Finds in SEARCHRESULTS a row where idcol == idval

        Returns dict
        '''

        logging.info(u'Retreving search result details for {}.'.format(idval))

        command = u'SELECT * FROM SEARCHRESULTS WHERE {}="{}"'.format(idcol, idval)

        result = self.execute(command)

        if result:
            return result.fetchone()
        else:
            return False

# pylama:ignore=W0401
