
from itertools import groupby
from operatory import itemgetter

class Timeline(object):

    def __init__(self, *args):

        self.events = args



    def ilines(self):
        
        min_ = min(e['start'] for e in self.events)
        max_ = max(e['end'] for e in self.events)

        key = itemgetter('activity')
        self.events.sort(key=key)
        for activity, events in groupby(self.events, key):
            
            for event in events:
                # get column positions
                pass
    
