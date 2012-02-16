from itertools import ifilter, imap, izip
from operator import itemgetter

def unitize_value(value, unit, default=None):
    '''Transform a value into a string, appending a unit. If the value is Falsy,
       then return the default value unitized.

       @param value : int|float|str
           the value to unitize
       @param unit : str
           the unit (h, ms, kg, etc...)
       @param default : stringable
           the value to use if value is falsy'''
    
    if not value:
        value = default

    return '%s %s' % (value, unit)

def timedelta(td):
    '''Return a string representation of a duration.

       @param td : timedelta
           the duration to convert to a string'''

    remainder = td.total_seconds()

    days, remainder = divmod(remainder, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, remainder = divmod(remainder, 60) 
    seconds, remainder = divmod(remainder, 1)
    milliseconds = 1000 * round(remainder, 3)

    components = imap(int, (days, hours, minutes, seconds))
    units = ('days', 'hours', 'minutes', 'seconds')

    components = izip(components, units)
    components = ifilter(itemgetter(0), components)
    components = list(unitize_value(c, u, 0) for c, u in components)

    if components:
        return ', '.join(components)

    if milliseconds:
        return '%d milliseconds' % milliseconds

    return '-'
        
