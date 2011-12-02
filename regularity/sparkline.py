

from stats import ibin_assignments

class Sparkline(object):

    def __init__(self, *args):
        '''Create a sparkline.

           @param args : positional arguments, int|float
               the data to plot'''
        
        if not args:
            raise ValueError('you must supply at least one datum')

        self.data = args

    def icolumns(self, max_steps, marker='+'):
        '''Return an iterator over the columns.

           @param max_steps : int
               the maximum number of steps in the y-axis
           @param marker : optional, str
               a single character to act as the marker'''

        # steps is at most max_steps
        # steps is at least 2
        max_datum = max(self.data)
        steps = min(max_steps, max_datum + 1)
        steps = max(2, steps)

        iassignments = ibin_assignments(steps, *self.data)

        bin_ranges = iassignments.next()

        for i in iassignments:
            yield marker * i 

