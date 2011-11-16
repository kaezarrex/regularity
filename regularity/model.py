import datetime
import pymongo
import uuid

class Model(object):

    def __init__(self, host='localhost'):
        connection = pymongo.Connection(host)
        self.db = connection.regularity
        self.uuid = uuid.uuid4().hex

    def previous(self, table, frequency, time=None):
        if time is None:
            time = datetime.datetime.utcnow()

        criteria = {
            'session' : self.uuid,
            'end' : { '$gt' : time - datetime.timedelta(seconds=2*frequency), '$lte' : time },
        }
        query = self.db[table].find(criteria)
        query = query.sort( 'end', -1)
        query = query.limit(1)
        previous = tuple(query)

        if previous:
            return previous[0]

        return None

    def update(self, table, activity, frequency, time=None):
        if time is None:
            time = datetime.datetime.utcnow()

        previous = self.previous(table, frequency, time=time)

        if previous and previous['activity'] == activity:
            previous['end'] = time
            self.db[table].save(previous)
        else:
            if previous:
                start = previous['end']
            else:
                start = time - datetime.timedelta(seconds=frequency)

            data = dict(
                session=self.uuid,
                activity=activity,
                start=start,
                end=time)
            self.db[table].save(data)

        
    def application(self, application_name, frequency, time=None):
        self.update('application', application_name, frequency, time=time)
        
    def window(self, window_name, frequency, time=None):
        self.update('window', window_name, frequency, time=time)

    def activity(self, activity_name, frequency, time=None):
        self.update('activity', activity_name, frequency, time=time)
        


