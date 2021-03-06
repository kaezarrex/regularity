
from itertools import chain, imap, izip
import math

def seconds_to_time(seconds):
    seconds = int(seconds)
    hours = seconds / 3600
    seconds = seconds - 3600 * hours
    minutes = seconds / 60
    seconds = seconds - 60 * minutes

    return '{:02d}:{:02d}'.format(hours, minutes)

def datetime_to_time_of_day(dt):
    '''Return the time of day of a datetime, expressed as seconds into the day.

       @param dt : datetime.datetime
           the datetime to convert'''

    return 3600 * dt.hour + 60 * dt.minute + dt.second

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

def isteps(steps, *args, **kwargs):
    '''Return an iterator of discretized steps over the range of args.

       @param steps : int
           the number of steps to build
       @param args : list(int|float)
           the data whose range will be discretized'''

    min_ = kwargs.get('min')
    if min_ is None:
        min_ = min(args)

    max_ = max(args)
    increment = float(max_ - min_) / steps

    step_max = min_
    for i in xrange(steps - 1):
        step_min = step_max
        step_max = step_min + increment
        yield step_min, step_max

    yield step_max, max_

def ibin_assignments(bins, *args, **kwargs):
    '''Return an iterator over the bin assignment for each datum in args.

       @param bins : int
           the number of bins
       @param args : list(int|float)
           the data to bin'''

    bin_ranges = list(isteps(bins, *args, **kwargs))

    yield bin_ranges
    for x in args:
        for i, (bin_min, bin_max) in enumerate(bin_ranges):
            
            if x < bin_max:
                break
        yield i

def ibin_range_assignments(bins, *args):
    '''Return an iterator over the bin assignments for each range in args.

       @param bins : int
           the number of bins
       @param args : list((int|float, int|float))
           the ranges to bin'''

    all_args = list(chain(*args))
    bin_ranges = list(isteps(bins, *all_args))
    n_bins = len(bin_ranges)

    yield bin_ranges
    for low, high in args:
        low_bin = None
        high_bin = None
        for i, (bin_min, bin_max) in enumerate(bin_ranges):
            
            if low_bin is None and low < bin_max:
                low_bin = i

            if high_bin is None and high < bin_max:
                high_bin = i

        if low_bin is None:
            low_bin = i

        if high_bin is None:
            high_bin = i

        if high_bin < low_bin:
            yield tuple(range(low_bin, n_bins) + range(high_bin + 1))
        else:
            yield tuple(range(low_bin, high_bin + 1))
           
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

def ibins_range(bins, *args):
    '''Bin the ranges (build a histogram) in args. The ranges are disretized 
       and a bin gets incremented each time a range overlaps with it.

       @param bins : int
           the number of bins
       @param args : list((int|float, int|float))
           the ranges to bin'''

    iassignments = ibin_range_assignments(bins, *args)

    bin_ranges = iassignments.next()
    bins = tuple(list() for i in xrange(bins))

    for bin_indices, x in izip(iassignments, args):
        for i in bin_indices:
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

def ibin_range_counts(bins, *args):
    '''Return just the counts of elements in a binning of args.

       @param bins : int
           the number of bins
       @param args : list((int|float, int|float))
           the ranges to bin'''

    for bin_range, bin_ in ibins_range(bins, *args):
        yield bin_range, len(bin_)

class EventStats(object):

    def __init__(self, *args):
        '''Create an EventStats object.

           @param args : list(dict)
               a list of events from the database'''

        if not args:
            raise ValueError('at least one event must be supplied')
        
        self.events = args

    def itime_ranges(self):
        '''Return an iterator over the time ranges of the events'''

        for event in self.events:
            yield event['start'], event['end']

    def itime_ranges_time_of_day_seconds(self):
        '''Return an iterator over the time ranges of the events, specified as
           the seconds into the day. Events that start before midnight, but end
           after will have their end time less than their start time. Values
           will be return with second resolution'''

        for start, end in self.itime_ranges():
            yield datetime_to_time_of_day(start), datetime_to_time_of_day(end)

    def idurations(self):
        '''Return an iterator over the durations as datetime.timedelta objects'''

        for start, end in self.itime_ranges():
            yield end - start

    def idurations_seconds(self):
        '''Return an iterator over the durations as floating point seconds.'''

        for duration in self.idurations():
            yield duration.total_seconds()

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

    def bin_counts_time_of_day(self, bins_):
        '''Return a heat map of activity, based on time of day.

           @param bins_ : int
               the number of bins to use'''

        time_ranges = self.itime_ranges_time_of_day_seconds()
        _counts = ibin_range_counts(bins_, *time_ranges)

        counts = list()
        for (start, end), count in _counts:
            start = seconds_to_time(start)
            end = seconds_to_time(end)
            counts.append(((start, end), count))
            
        return counts
