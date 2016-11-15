class Conversions():

    @staticmethod
    def human_file_size(value, format='%.1f'):
        suffix = ('kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')

        base = 1024
        bytes = float(value)

        if bytes == 1 and not gnu:
            return '1 Byte'
        elif bytes < base :
            return '%d Bytes' % bytes

        for i,s in enumerate(suffix):
            unit = base ** (i+2)
            if bytes < unit:
                return (format + ' %s') % ((base * bytes / unit), s)
        return (format + ' %s') % ((base * bytes / unit), s)
