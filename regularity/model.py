import datetime
import pymongo

class Model(object):

    CONTIGUITY_THRESHOLD = 5 # seconds

    def __init__(self, host='localhost'):
        '''Create a connection to mongoDB

           @param host : optional, str, the host of the mongoDB server'''

        connection = pymongo.Connection(host)
        self.db = connection.regularity

    def _build_event(self, timeline_name, name, start, end):
        '''Helper function for building an event object to be saved to the
           database.

           @param timeline_name : str
               the name of the timeline to scan for overlapping activities
           @param name : str
               the name of the activity to create
           @param start : datetime
               the start time of the activity, in UTC
           @param end : datetime
               the end time of the activity, in UTC'''

        data = dict(
            timeline=timeline_name,
            name=name,
            start=start,
            end=end,
        )

        return data

    def overlapping(self, start, end, buffer_=None, **kwargs):
        '''Return timeline events that overlap with the time denoted by start
           and end
           
           @param start : datetime
               the start time of the activity
           @param end : datetime
               the end time of the activity
           @param buffer : optional, int
               the number of seconds to buffer out the time range, useful for 
               catching events that barely don't overlap, defaults to 5 seconds
           @param kwargs : optional
               additional criteria for the query'''

        if buffer_ is None:
            buffer_ = self.CONTIGUITY_THRESHOLD
        buffer_ = datetime.timedelta(seconds=buffer_)

        start = start - buffer_
        end = end + buffer_

        criteria = kwargs
        criteria.update({
            '$nor' : [
                { 'start' : { '$gt' : end } },
                { 'end' : { '$lt' : start } },
            ]
        })
        query = self.db.events.find(criteria)
        query = query.sort('end', 1)
        overlapping = tuple(query)

        return overlapping

    def events(self, **kwargs):
        '''Perform a general query for events. By default, will return all
           events unless filtering criteria are specified in kwargs.
           
           @param kwargs : 
               mapping from keyword to list of values - valid keys are:

               name - the name of the event
               timeline - the name of the timeline'''

        criteria = dict()

        name = kwargs.get('name')
        if name:
            criteria['name'] = name

        timeline = kwargs.get('timeline')
        if timeline:
            criteria['timeline'] = timeline

        data = self.db.events.find(criteria)
        return tuple(data)

    def _log(self, timeline_name, name, start, end, union=True):
        '''Log the activity into the database and optionally union it with any 
           activities on the same timeline that overlap and have the same 
           activity name.
           
           @param timeline_name : str
               the name of the timeline to scan for overlapping activities
           @param name : str
               the name of the activity to match up
           @param start : datetime
               the start time of the activity
           @param end : datetime
               the end time of the activity
           @param union : bool
               optional, whether the event should be unioned with other events
               of the same timeline and name, defaults to True'''

        data = self._build_event(timeline_name, name, start, end)

        if union:
            extra_criteria = {
                'timeline' : timeline_name,
                'name' : name
            }
            overlapping_activities = self.overlapping(start, end, **extra_criteria)

            if overlapping_activities:
                # consolidate all the overlapping activities into one
                # preserve the id of the first activity
                data['_id'] = overlapping_activities[0]['_id']
                data['start'] = min(start, *(a['start'] for a in overlapping_activities))
                data['end'] = max(end, *(a['end'] for a in overlapping_activities))

                for a in overlapping_activities:
                    self.db.events.remove(a)

        self.db.events.save(data)
        return data

    def truncate(self, timeline_name, name, start, end):
        '''Truncate all activities on the same timeline that overlap and are
           not the same activity.
           
           @param timeline_name : str
               the name of the timeline to scan for overlapping activities
           @param name : str
               the name of the activity to match up
           @param start : datetime
               the start time of the activity
           @param end : datetime
               the end time of the activity'''

        extra_criteria = {
            'timeline' : timeline_name,
            'name' : { '$ne' : name },
        }
        overlapping_activities = self.overlapping(start, end, **extra_criteria)

        for a in overlapping_activities:
            if a['end'] < end:
                a['end'] = start

                self.db.events.save(a)

            elif a['start'] > start:
                a['start'] = end

                self.db.events.save(a)

            else:
                # split the activity into two
                activity1 = self._build_event(timeline_name, a['name'], a['start'], start)
                activity2 = self._build_event(timeline_name, a['name'], end, a['end'])

                self.db.events.remove(a)
                self.db.events.save(activity1)
                self.db.events.save(activity2)

    def log(self, timeline_name, name, start=None, end=None, **kwargs):
        '''Log the occurence of an activity to the specified timeline.

           @param timeline_name : str
               name of the timeline
           @param name : str
               name of the activity
           @param start : optional, datetime
               the start time of the activity, defaults to now
           @param end : optional, datetime
               the end time of the activity, defaults to start'''

        if start is None:
            start = datetime.datetime.utcnow()

        if end is None:
            end = start

        union = kwargs.get('union', True)
        truncate = kwargs.get('truncate', False)

        data = self._log(timeline_name, name, start, end, union=union)
        if truncate:
            self.truncate(timeline_name, name, data['start'], data['end'])

        return data


    def update(self, timeline_name, name):
        '''Log the continuance of an ongoing activity to the specified timeline

           @param timeline_name : str
               the name of the timeline
           @param name : str
               the name of the activity'''

        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(seconds=self.CONTIGUITY_THRESHOLD)
        
        data = self.log(timeline_name, name, start=start, end=end)
        return data
        

