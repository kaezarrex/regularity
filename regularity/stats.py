
from itertools import imap
import math

def mean(*args):
    '''Return the mean of args.

       @param args : list(ind|float)
          the list of numbers to compute the mean for'''
    
    return sum(imap(float, args)) / len(args) 


def std(*args):
    '''Return the standard deviation of args.
       
       @param args : list(int|float)
           the list of numbers to compute the standard deviation for'''
    
    mean_ = mean(*args)

    squared_differences = ((x - mean_)**2 for x in args)
    return math.sqrt(sum(squared_differences) / len(args))

def discretize(levels, *args):
    '''Discretizes a list of values to a list of levels.

       @param levels : int
           the number of levels to discretize to
       @param args : list(int|float)
           the numbers to discretize'''

    min_ = float(min(data))
    max_ = float(max(data))
    increment = (max_ - min_) / levels

    thresholds = tuple(min_ + i * increment for i in xrange(1, levels)) + (max_,)

    def level(x):
        for i, threshold in enumerate(thresholds):
            if x <= threshold:
                return i
        return levels - 1

    return tuple(level(d) for d in data)


class EventStats(object):

    def __init__(self, *args):
        '''Create an EventStats object.

           @param args : list(dict)
               a list of events from the database'''

        if not args:
            raise ValueError('at least one event must be supplied')
        
        self.events = args

    def idurations(self):
        '''Return an iterator over the durations as datetime.timedelta objects'''

        timedeltas = (e['end'] - e['start'] for e in self.events)
        return timedeltas

    def idurations_seconds(self):
        '''Return an iterator over the durations as floating point seconds.'''

        durations = (td.total_seconds() for td in self.idurations())
        return durations

    def min_duration(self):
        '''Return the minimum duration.'''

        return min(self.idurations_seconds())

    def max_duration(self):
        '''Return the maximum duration.'''
        
        return max(self.idurations_seconds())

    def mean_duration(self):
        '''Return the mean duration'''

        return mean(*self.idurations_seconds())

    def std_duration(self):
        '''Return the standard deviation of durations'''

        return std(*self.idurations_seconds())


