import datetime
import pymongo
import uuid

def union(*activities):
    pass


class Model(object):

    CONTIGUITY_THRESHOLD = 5 # seconds

    def __init__(self, host='localhost'):
        '''Create a connection to mongoDB

           @param host : optional, str
               the host of the mongoDB server'''

        connection = pymongo.Connection(host)
        self.db = connection.regularity
        self.uuid = uuid.uuid4().hex

    def overlapping(self, timeline, start, end, buffer_=None, **kwargs):
        '''Return timeline events that overlap with the time denoted by start
           and end
           
           @param timeline : str
               the timeline to scan for overlapping activities
           @param start : datetime
               the start time of the activity
           @param end : datetime
               the end time of the activity
           @param buffer : optional, int
               the number of seconds to buffer out
               the time range, useful for catching events that 
               barely don't overlap, defaults to 5 seconds
           @param kwargs : optional
               additional criteria for the query'''

        if buffer_ is None:
            buffer_ = self.CONTIGUITY_THRESHOLD
        buffer_ = datetime.timedelta(seconds=buffer_)

        start = start - buffer_
        end = end + buffer_

        criteria = kwargs
        criteria.update({
            'timeline' : timeline,
            '$nor' : [
                { 'start' : { '$gt' : end } },
                { 'end' : { '$lt' : start } },
            ]
        })
        query = self.db.timelines.find(criteria)
        overlapping = tuple(query)

        return overlapping

    def union(self, timeline, activity, start, end):
        '''Union this activity with any activities on the same timeline that 
           overlap and are the same activity.
           
           @param timeline : str
               the timeline to scan for overlapping activities
           @param activity : str
               the name of the activity to match up
           @param start : datetime
               the start time of the activity
           @param end : datetime
               the end time of the activity'''

        extra_criteria = {
            'activity' : activity
        }
        overlapping_activities = self.overlapping(timeline, start, end, **extra_criteria)

        if overlapping_activities:
            start = min(start, *(a['start'] for a in overlapping_activities))
            end = max(end, *(a['end'] for a in overlapping_activities))

            for a in overlapping_activities:
                self.db.timelines.remove(a)

        data = dict(
            session=self.uuid,
            timeline=timeline,
            activity=activity,
            start=start,
            end=end,
        )

        self.db.timelines.save(data)
        return data

    def truncate(self, timeline, activity, start, end):
        '''Truncate all activities on the same timeline that overlap and are
           not the same activity.
           
           @param timeline : str
               the timeline to scan for overlapping activities
           @param activity : str
               the name of the activity to match up
           @param start : datetime
               the start time of the activity
           @param end : datetime
               the end time of the activity'''

        extra_criteria = {
            'activity' : { '$ne' : activity },
        }
        overlapping_activities = self.overlapping(timeline, start, end, **extra_criteria)

        for a in overlapping_activities:
            if a['end'] < end:
                a['end'] = start

                self.db.timelines.save(a)

            elif a['start'] > start:
                a['start'] = end

                self.db.timelines.save(a)

            else:
                # split the activity into two
                activity1 = dict(
                    session=self.uuid,
                    timeline=timeline,
                    activity=a['activity'],
                    start=a['start'],
                    end=start
                )
                activity2 = dict(
                    session=self.uuid,
                    timeline=timeline,
                    activity=a['activity'],
                    start=end,
                    end=a['end'],
                )

                self.db.timelines.remove(a)
                self.db.timelines.save(activity1)
                self.db.timelines.save(activity2)

    def log(self, timeline, activity, start=None, end=None):
        '''Log the occurence of an activity to the specified timeline.

           @param timeline : str
               name of the timeline
           @param activity : str
               name of the activity
           @param start : optional, datetime
               the start time of the activity, defaults to now
           @param end : optional, datetime
               the end time of the activity, defaults to start'''

        if start is None:
            start = datetime.datetime.utcnow()

        if end is None:
            end = start

        data = self.union(timeline, activity, start, end)
        self.truncate(timeline, activity, data['start'], data['end'])


    def update(self, timeline, activity):
        '''Log the continuance of an ongoing activity to the specified timeline

           @param timeline : str
               the name of the timeline
           @param activity : str
               the name of the activity'''

        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(seconds=self.CONTIGUITY_THRESHOLD)
        
        self.log(timeline, activity, start=start, end=end)
        


