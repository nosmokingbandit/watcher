import logging

from core import sqldb

logging = logging.getLogger(__name__)


class Status(object):

    def __init__(self):
        self.sql = sqldb.SQL()

    def searchresults(self, guid, status):
        ''' Marks searchresults status
        :param guid: str download link guid
        :param status: str status to set

        If guid is in SEARCHRESULTS table, marks it as Bad.

        Returns Bool on success/fail
        '''

        TABLE = u'SEARCHRESULTS'

        logging.info(u'Marking guid {} as {}.'.format(guid, status))

        if self.sql.row_exists(TABLE, guid=guid):

            # Mark bad in SEARCHRESULTS
            logging.info(u'Marking {} as {} in SEARCHRESULTS.'.format(guid, status))
            if not self.sql.update(TABLE, 'status', status, guid=guid):
                logging.info(u'Setting SEARCHRESULTS status of {} to {} failed.'.format(guid, status))
                return False
            else:
                logging.info(u'Successfully marked {} as {} in SEARCHRESULTS.'.format(guid, status))
                return True
        else:
            logging.info(u'Guid {} not found in SEARCHRESULTS.'.format(guid))
            return False

    def markedresults(self, guid, status, imdbid=None):
        ''' Marks markedresults status
        :param guid: str download link guid
        :param status: str status to set
        :param imdbid: str imdb identification number   <optional>

        imdbid can be None

        If guid is in MARKEDRESULTS table, marks it as status.
        If guid not in MARKEDRSULTS table, created entry. Requires imdbid.

        Returns Bool on success/fail
        '''

        TABLE = u'MARKEDRESULTS'

        if self.sql.row_exists(TABLE, guid=guid):
            # Mark bad in MARKEDRESULTS
            logging.info(u'Marking {} as {} in MARKEDRESULTS.'.format(guid, status))
            if not self.sql.update(TABLE, 'status', status, guid=guid):
                logging.info(u'Setting MARKEDRESULTS status of {} to {} failed.'.format(guid, status))
                return False
            else:
                logging.info(u'Successfully marked {} as {} in MARKEDRESULTS.'.format(guid, status))
                return True
        else:
            logging.info(u'Guid {} not found in MARKEDRESULTS, creating entry.'.format(guid))
            if imdbid:
                DB_STRING = {}
                DB_STRING['imdbid'] = imdbid
                DB_STRING['guid'] = guid
                DB_STRING['status'] = status
                if self.sql.write(TABLE, DB_STRING):
                    logging.info(u'Successfully created entry in MARKEDRESULTS for {}.'.format(guid))
                    return True
                else:
                    logging.info(u'Unable to create entry in MARKEDRESULTS for {}.'.format(guid))
                    return False
            else:
                logging.info(u'Imdbid not supplied or found, unable to add entry to MARKEDRESULTS.')
                return False

    def mark_bad(self, guid, imdbid=None):
        ''' Marks search result as Bad
        :param guid: str download link for nzb/magnet/torrent file.

        Calls self method to update both db tables
        Tries to find imdbid if not supplied.
        If imdbid is available or found, executes self.movie_status()

        Returns bool
        '''

        if not self.searchresults(guid, 'Bad'):
            return 'Could not mark guid in SEARCHRESULTS. See logs for more information.'

        # try to get imdbid
        if imdbid is None:
            result = self.sql.get_single_search_result('guid', guid)
            if not result:
                return False
            else:
                imdbid = result['imdbid']

        if not self.movie_status(imdbid):
            return False

        if not self.markedresults(guid, 'Bad', imdbid=imdbid):
            return False
        else:
            return True

    def movie_status(self, imdbid):
        ''' Updates Movie status.
        :param imdbid: str imdb identification number (tt123456)

        Updates Movie status based on search results.
        Always sets the status to the highest possible level.

        Returns bool on success/failure.
        '''

        current_status = self.sql.get_movie_details('imdbid', imdbid).get('status')

        if current_status == 'Disabled':
            return True

        result_status = self.sql.get_distinct('SEARCHRESULTS', 'status', 'imdbid', imdbid)
        if result_status is False:
            logging.info(u'Could not get SEARCHRESULT statuses for {}'.format(imdbid))
            return False
        elif result_status is None:
            status = u'Wanted'
        else:
            if 'Finished' in result_status:
                status = u'Finished'
            elif 'Snatched' in result_status:
                status = u'Snatched'
            elif 'Available' in result_status:
                status = u'Found'
            else:
                status = u'Wanted'

        logging.info(u'Setting MOVIES {} status to {}.'.format(imdbid, status))
        if self.sql.update('MOVIES', 'status', status, imdbid=imdbid):
            return True
        else:
            logging.info(u'Could not set {} to {}'.format(imdbid, status))
            return False
