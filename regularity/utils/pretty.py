from itertools import ifilter
from operator import itemgetter

def unitize_value(value, unit):
    '''Transform a value into a string, appending a unit. If the value is Falsy,
       then return None

       @param value : int|float|str
           the value to unitize
       @param unit : str
           the unit (h, ms, kg, etc...)'''
    
    if value:
        return '%s%s' % (value, unit)

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

    days = unitize_value(days, 'd')
    hours = unitize_value(hours, 'h')
    minutes = unitize_value(minutes, 'm')
    seconds = unitize_value(seconds, 's')
    milliseconds = unitize_value(milliseconds, 'ms')

    if days:
        components = (days, hours, minutes)

    elif hours:
        components = (hours, minutes, seconds)

    elif minutes:
        components = (minutes, seconds)

    elif seconds:
        components = (seconds,)

    elif milliseconds:
        components = (milliseconds,)

    else:
        components = ('-',)

    return ''.join(components)


