from itertools import ifilter
from operator import itemgetter

def timedelta(td):
    '''Return a string representation of a duration.

       @param td : timedelta
           the duration to convert to a string'''

    remainder = int(td.total_seconds())

    days, remainder = divmod(remainder, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60) 

    components = ifilter(itemgetter(0), ((days, 'd'), (hours, 'h'), (minutes, 'm'), (seconds, 's')))
    return ''.join('%d%s' % c for c in components)

