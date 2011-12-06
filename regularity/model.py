import datetime
import pymongo
import uuid

class Model(object):

    CONTIGUITY_THRESHOLD = 5 # seconds

    def __init__(self, host='localhost'):
        '''Create a connection to mongoDB

           @param host : optional, str, the host of the mongoDB server'''

        connection = pymongo.Connection(host)
        self.db = connection.regularity
        self.uuid = uuid.uuid4().hex

    def overlapping(self, start, end, buffer_=None, **kwargs):
        '''Return timeline events that overlap with the time denoted by start
           and end
           
           @param timeline_name : str
               the name of the timeline to scan for overlapping activities
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
            criteria['name'] = {
                '$in' : name
            }

        timeline = kwargs.get('timeline')
        if timeline:
            criteria['timeline'] = {
                '$in' : timeline
            }

        data = self.db.events.find(criteria)
        return tuple(data)

    def union(self, timeline_name, name, start, end):
        '''Union this activity with any activities on the same timeline that 
           overlap and have the same activity name.
           
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
            'name' : name
        }
        overlapping_activities = self.overlapping(start, end, **extra_criteria)

        data = dict(
            session=self.uuid,
            timeline=timeline_name,
            name=name,
            start=start,
            end=end,
        )

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
                activity1 = dict(
                    session=self.uuid,
                    timeline=timeline_name,
                    name=a['name'],
                    start=a['start'],
                    end=start
                )
                activity2 = dict(
                    session=self.uuid,
                    timeline=timeline_name,
                    name=a['name'],
                    start=end,
                    end=a['end'],
                )

                self.db.events.remove(a)
                self.db.events.save(activity1)
                self.db.events.save(activity2)

    def timeline(self, timeline_name):
        '''Get the timeline with the given name.

           @param timeline_name : str
               the name of the timeline to get'''

        criteria = {
            'name' : timeline_name
        }
        data = self.db.timelines.find_one(criteria)

        if not data:
            self.db.timelines.insert(dict(
                name=timeline_name,
            ))
            data = self.db.timelines.find_one(criteria)

        return data

    def log(self, timeline_name, name, start=None, end=None):
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

        timeline = self.timeline(timeline_name)
        data = self.union(timeline_name, name, start, end)

        if not timeline.get('allow_overlap', True):
            self.truncate(timeline_name, name, data['start'], data['end'])

        return data


    def update(self, timeline_name, name):
        '''Log the continuance of an ongoing activity to the specified timeline

           @param timeline_name : str, the name of the timeline
           @param name : str, the name of the activity'''

        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(seconds=self.CONTIGUITY_THRESHOLD)
        
        data = self.log(timeline_name, name, start=start, end=end)
        return data
        

