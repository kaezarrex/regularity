import datetime
import pymongo
import uuid

def union(*activities):
    pass


class Model(object):

    CONTIGUITY_THRESHOLD = 5 # seconds

    def __init__(self, host='localhost'):
        connection = pymongo.Connection(host)
        self.db = connection.regularity
        self.uuid = uuid.uuid4().hex

    def overlapping(self, timeline, start, end, buffer_=None, **kwargs):

        if buffer_ is None:
            buffer_ = self.CONTIGUITY_THRESHOLD
        buffer_ = datetime.timedelta(seconds=buffer_)

        start = start - buffer_
        end = end + buffer_

        criteria = kwargs
        criteria.update({
#            'session' : self.uuid,
            'timeline' : timeline,
            '$or' : [
                { 'start' : { '$lte' : start }, 'end' : { '$gte' : end } },
                { 'start' : { '$gte' : start }, 'start' : { '$lte' : end } },
                { 'end' : { '$gte' : start }, 'end' : { '$lte' : end } },
            ]
        })
        query = self.db.timelines.find(criteria)
        query = query.sort( 'end', -1)
        query = query.limit(1)
        overlapping = tuple(query)

        return overlapping

    def union(self, timeline, activity, start, end):
        '''Union this activity with any activities on the same timeline that 
           overlap and are the same activity.'''

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
           not the same activity.'''

        extra_criteria = {
            'activity' : { '$ne' : activity },
        }
        overlapping_activities = self.overlapping(timeline, start, end, **extra_criteria)

        for activity in overlapping_activities:
            if activity['end'] < end:
                activity['end'] = start

                self.db.timelines.save(activity)

            elif activity['start'] > start:
                activity['start'] = end

                self.db.timelines.save(activity)

            else:
                # split the activity into two
                activity1 = dict(activity)
                activity2 = dict(activity)

                activity1['end'] = start
                activity2['start'] = end

                self.db.timelines.remove(activity)
                self.db.timelines.save(activity1)
                self.db.timelines.save(activity2)

    def log(self, timeline, activity, start=None, end=None):
        if start is None:
            start = datetime.datetime.utcnow()

        if end is None:
            end = start

        data = self.union(timeline, activity, start, end)
        self.truncate(timeline, activity, data['start'], data['end'])


    def update(self, timeline, activity):
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(seconds=self.CONTIGUITY_THRESHOLD)
        
        self.log(timeline, activity, start=start, end=end)
        


