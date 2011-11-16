import datetime
import pymongo
import uuid

class Model(object):

    CONTIGUITY_THRESHROLD = 10 # seconds

    def __init__(self, host='localhost'):
        connection = pymongo.Connection(host)
        self.db = connection.regularity
        self.uuid = uuid.uuid4().hex

    def previous(self, timeline, start):
        criteria = {
            'session' : self.uuid,
            'timeline' : timeline,
            'end' : { '$gt' : start - datetime.timedelta(seconds=self.CONTIGUITY_THRESHROLD), '$lte' : start },
        }
        query = self.db.timelines.find(criteria)
        query = query.sort( 'end', -1)
        query = query.limit(1)
        previous = tuple(query)

        if previous:
            return previous[0]

        return None

    def update(self, timeline, activity, start=None, end=None):
        if start is None:
            start = datetime.datetime.utcnow()

        if end is None:
            end = start

        previous = self.previous(timeline, start)
        #todo see if there are overlaps between this and a possible next

        if previous and previous['activity'] == activity:
            previous['end'] = start
            self.db.timelines.save(previous)
        else:
            if previous:
                start = previous['end']

            data = dict(
                session=self.uuid,
                timeline=timeline,
                activity=activity,
                start=start,
                end=end)
            self.db.timelines.save(data)
        


