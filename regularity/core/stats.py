from collections import Counter
import datetime
from itertools import imap
import math
from operator import itemgetter

def _mean(args):
    '''Return the mean of args.

       @param args : list(int|float)
          the list of numbers to compute the mean for'''
    
    if not args:
        return None

    return sum(imap(float, args)) / len(args) 


def _std(args, return_mean=False):
    '''Return the standard deviation of args.
       
       @param args : list(int|float)
           the list of numbers to compute the standard deviation for'''

    if not args:
        if return_mean:
            return None, None
        return None
    
    mean = _mean(args)

    squared_differences = ((x - mean)**2 for x in args)
    std = math.sqrt(sum(squared_differences) / len(args))

    if return_mean:
        return mean, std

    return std

def _counts(iterable):
    '''Return the counts of elements in the iterable, in descending order.

       @param iterable : iterable
           the iterable of elements'''

    counts = Counter(iterable)
    return sorted(counts.iteritems(), key=itemgetter(1), reverse=True)

class RegularityStatistics(object):

    def __init__(self, dots=None, dashes=None, pendings=None):
        '''Create the statitics calculator.

           @param dots : optional, list(dict)
               the dots to compute statistics for
           @param dashes : optional, list(dict)
               the dashes to compute statistics for
           @param pendings : optional, list(dict)
               the pendings to compute statistics for'''

        if dots is not None:
            self.dots = dots
        else:
            self.dots = list()

        if dashes is not None:
            self.dashes = dashes
        else:
            self.dashes = list()
            
        if pendings is not None:
            self.pendings = pendings
        else:
            self.pendings = list()

    @property
    def dot_counts(self):
        '''Return a tuple of (name, count) for in descending count order.'''

        return _counts(d['name'].lower() for d in self.dots)

    @property
    def dash_counts(self):
        '''Return a tuple of (name, count) for in descending count order.'''

        return _counts(d['name'].lower() for d in self.dashes)

    @property
    def pending_counts(self):
        '''Return a tuple of (name, count) for in descending count order.'''

        return _counts(p['name'].lower() for p in self.pendings)

    @property
    def dash_aggregate_duration(self):
        '''Return statistics on the durations of the dashes.'''

        durations = (d['end'] - d['start'] for d in self.dashes)
        durations = tuple(d.total_seconds() for d in durations)

        mean, std = _std(durations, return_mean=True)

        if mean is not None:
            mean = datetime.timedelta(seconds=mean)

        if std is not None:
            std = datetime.timedelta(seconds=std)

        return dict(
            mean=mean,
            std=std
        )



