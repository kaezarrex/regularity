
from itertools import imap, izip
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

def isteps(steps, *args):
    '''Return an iterator of discretized steps over the range of args.

       @param steps : int
           the number of steps to build
       @param args : list(int|float)
           the data whose range will be discretized'''

    min_ = min(args)
    max_ = max(args)
    increment = float(max_ - min_) / steps

    step_max = min_
    for i in xrange(steps - 1):
        step_min = step_max
        step_max = step_min + increment
        yield step_min, step_max

    yield step_max, max_

def ibin_assignments(bins, *args):
    '''Return an iterator over the bin assignment for each datum in args.

       @param bins : int
           the number of bins
       @param args : list(int|float)
           the data to bin'''

    bin_ranges = list(isteps(bins, *args))

    yield bin_ranges
    for x in args:
        for i, (bin_min, bin_max) in enumerate(bin_ranges):
            
            if x < bin_max:
                break
        yield i
           
def ibins(bins, *args):
    '''Bin the data (build a histogram) in args.

       @param bins : int
           the number of bins
       @param args : list(int|float)
           the data to bin'''

    iassignments = ibin_assignments(bins, *args)

    bin_ranges = iassignments.next()
    bins = tuple(list() for i in xrange(bins))

    for i, x in izip(iassignments, args):
        bins[i].append(x)

    return izip(bin_ranges, bins)

def ibin_counts(bins, *args):
    '''Return just the counts of elements in a binning of args.

       @param bins : int
           the number of bins
       @param args : list(int|float)
           the data to bin'''

    for bin_range, bin_ in ibins(bins, *args):
        yield bin_range, len(bin_)

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

    def bins_duration(self, bins_):
        '''Return a binning of the durations.

           @param bins_ : int
               the number of bins to use'''

        return list(ibins(bins_, *self.idurations_seconds()))

    def bin_counts_duration(self, bins_):
        '''Return a count of the binning of the durations.

           @param bins_ : int
               the number of bins to use'''

        return list(ibin_counts(bins_, *self.idurations_seconds()))
        
