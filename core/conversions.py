class Conversions():
    ''' Coverts data to human-readable formats. '''

    @staticmethod
    def human_file_size(value, format='%.1f'):
        ''' Converts bytes to human readable size.
        :param value: int file size in bytes

        Returns str file size in highest appropriate suffix.
        '''

        suffix = ('kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')

        base = 1024
        bytes = float(value)

        if bytes == 1:
            return '1 Byte'
        elif bytes < base:
            return '%d Bytes' % bytes

        for i, s in enumerate(suffix):
            unit = base ** (i + 2)
            if bytes < unit:
                return (format + ' %s') % ((base * bytes / unit), s)
        return (format + ' %s') % ((base * bytes / unit), s)

    @staticmethod
    def human_datetime(dt):
        ''' Converts datetime object into human-readable format.
        :param dt: datetime object

        Returns str date formatted as "Monday, Jan 1st, at 12:00" (24hr time)
        '''

        return dt.strftime('%A, %b %d, at %H:%M')
