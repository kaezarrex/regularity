from datetime import datetime, timedelta
from itertools import groupby

import clutter

from event_view import EventView

class TimePeriodBox(clutter.Box):

    def __init__(self, model, start=None, end=None):
        '''Constructs a view over a certain time period.

           @param model : regularity.model.Model
               the connection to mongo db
           @param start : optional, datetime.datetime
               the beginning of the period of interest, defaults to the
               beginning of today, (in UTC time)
           @param end : datetime.datetime
               the end of the period of interest, defaults to the end of the 
               day specified by start'''

        self.layout = clutter.BoxLayout()
        self.layout.set_vertical(True)

        super(TimePeriodBox, self).__init__(self.layout)

        if not start:
            start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        if not end:
            end = start.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        if start >= end:
            raise ValueError('end must be after start')

        self.model = model
        self.start = start
        self.end = end

        events = self.model.overlapping(self.start, self.end)
        events = list(events)
        
        # group the events by activity
        events.sort(key=lambda e : (e['timeline'], e['name'], e['start']))
        for i, (name, events) in enumerate(groupby(events, lambda e : e['name'])):
            event_view = EventView(self.model, list(events), self.start, self.end)
            self.layout.pack(event_view, False, True, False, clutter.BOX_ALIGNMENT_START, clutter.BOX_ALIGNMENT_START)

        
