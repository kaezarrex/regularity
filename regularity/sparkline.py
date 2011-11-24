

from stats import ibin_assignments

class Sparkline(object):

    def __init__(self, *args):
        '''Create a sparkline.

           @param args : positional arguments, int|float
               the data to plot'''
        
        if not args:
            raise ValueError('you must supply at least one datum')

        self.data = args

    def icolumns(self, steps, marker='+'):
        '''Return an iterator over the columns.

           @param steps : int
               the number of steps in the y-axis
           @param marker : optional, str
               a single character to act as the marker'''

        iassignments = ibin_assignments(steps, *self.data)

        bin_ranges = iassignments.next()

        for i in iassignments:
            yield marker * i 

