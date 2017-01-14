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


class Comparisons():

    @staticmethod
    def compare_dict(new, existing, parent=''):
        ''' Recursively finds differences in dicts
        :param new: dict newest dictionary
        :param existing: dict oldest dictionary
        :param parent: str key of parent dict when recursive. DO NOT PASS.

        Recursively compares 'new' and 'existing' dicts. If any value is different,
            stores the new value as {k: v}. If a recursive difference, stores as
            {parent: {k: v}}

        Param 'parent' is only used internally for recurive comparisons. Do not pass any
            value as parent. Weird things may happen.

        Returns dict
        '''

        diff = {}
        for k in new.keys():
            if k not in existing.keys():
                diff.update({k: new[k]})
            else:
                if type(new[k]) is dict:
                    diff.update(Comparisons.compare_dict(new[k], existing[k], parent=k))
                else:
                    if new[k] != existing[k]:
                        diff.update({k: new[k]})
        if parent and diff:
            return {parent: diff}
        else:
            return diff
