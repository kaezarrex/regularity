
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

def idiscretize(min_, max_, levels):
    '''Build a list of thresholds to range between min_ and max_.

       @param min_ : int|float
           the minimum value to account for
       @param max_ : int|float
           the maximum value to account for
       @param n : int
           the number of thresholds to build'''

    increment = float(max_ - min_) / levels

    bin_max = min_
    for i in xrange(levels - 1):
        bin_min = bin_max
        bin_max = bin_min + increment
        yield bin_min, bin_max

    yield bin_max, max_
           
def ibins(bins, *args):
    '''Bin the data (build a histogram) in args.

       @param bins : int
           the number of bins
       @param args : list(int|float)
           the data to bin'''

    min_ = min(args)
    max_ = max(args)

    bin_ranges = list(idiscretize(min_, max_, bins))
    bins = tuple(list() for i in xrange(bins))

    for x in args:
        for i, (bin_min, bin_max) in enumerate(bin_ranges):
            
            if x < bin_max:
                break

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
        
