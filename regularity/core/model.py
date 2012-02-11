import datetime
import pymongo

class Model(object):

    CONTIGUITY_THRESHOLD = 5 # seconds

    def __init__(self, host='localhost', port=27017, user=None, password=None, database='regularity'):
        '''Create a connection to mongoDB

           @param host : optional, str
               the host of the mongoDB server'''

        connection = pymongo.Connection(host=host, port=port)
        db = pymongo.database.Database(connection, database)

        if user and password:
            success = db.authenticate(user, password)
            if not success:
                raise BaseException('could not authenticate')

        self.db = db

    def _build_dot(self, client, timeline_name, name, time):
        '''Helper function for building a dot object to be saved to the
           database.

           @param client : str
               the name of the client to which the event belongs
           @param timeline_name : str
               the name of the timeline to scan for overlapping activities
           @param name : str
               the name of the activity to create
           @param time : datetime
               the time of the dot, in UTC'''

        return dict(
            client=client,
            timeline=timeline_name,
            name=name,
            time=time,
        )


    def _build_event(self, client, timeline_name, name, start, end):
        '''Helper function for building an event object to be saved to the
           database.

           @param client : str
               the name of the client to which the event belongs
           @param timeline_name : str
               the name of the timeline to scan for overlapping activities
           @param name : str
               the name of the activity to create
           @param start : datetime
               the start time of the activity, in UTC
           @param end : datetime
               the end time of the activity, in UTC'''

        data = dict(
            client=client,
            timeline=timeline_name,
            name=name,
            start=start,
            end=end,
        )

        return data
    
    def _build_pending(self, client, timeline_name, name, start):
        '''Helper function for building a pending object to be saved to the 
           database.

           @param client : str
               the name of the client to which the event belongs
           @param timeline_name : str
               the name of the timeline to scan for overlapping activities
           @param name : str
               the name of the activity to create
           @param start : datetime
               the start time of the activity, in UTC'''
        
        data = dict(
            client=client,
            timeline=timeline_name,
            name=name,
            start=start,
        )

        return data

    def client(self):
        '''Create a new client.'''

        client = dict()
        self.db.clients.insert(client)
        return client

    def dot(self, client, timeline_name, name, time=None, **kwargs):
        '''Log the occurence of an instaneous activity to the specified
           timeline.

           @param client : str
               the name of the client to which the event belongs
           @param timeline_name : str
               name of the timeline
           @param name : str
               name of the activity
           @param time : optional, datetime
               the time of the activity, defaults to now'''

        if time is None:
            time = datetime.datetime.utcnow()

        dot = self._build_dot(client, timeline_name, name, time)
        self.db.dots.insert(dot)
        
        return dot

    def dots(self, client, limit=10, **kwargs):
        '''Perform a general query for dots. By default, will return all events 
           unless filtering criteria are specified in kwargs.
           
           @param client : str
               the id of the client to which the event belongs
           @param limit : optional, int
                retrieve this many most-recent documents, defaults to 10
           @param kwargs : 
               mapping from keyword to list of values - valid keys are:

               name - the name of the event
               timeline - the name of the timeline'''

        criteria = {
            'client' : client
        }

        name = kwargs.get('name')
        if name:
            criteria['name'] = name

        timeline = kwargs.get('timeline')
        if timeline:
            criteria['timeline'] = timeline

        query = self.db.dots.find(criteria)
        query = query.sort('time', -1)
        query = query.limit(limit)

        return tuple(query)[::-1]

    def overlapping_dots(self, client, start, end, buffer_=None, **kwargs):
        '''Return timeline dots that overlap with the time denoted by start
           and end
           
           @param client : str
               the name of the client to which the event belongs
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
            'client' : client,
            '$nor' : [
                { 'time' : { '$gt' : end } },
                { 'time' : { '$lt' : start } },
            ]
        })
        query = self.db.dots.find(criteria)
        query = query.sort('time', 1)
        overlapping = tuple(query)

        return overlapping

    def dash(self, client, timeline_name, name, start=None, end=None, **kwargs):
        '''Log the occurence of a ranged activity to the specified timeline.

           @param client : str
               the name of the client to which the event belongs
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

        dash = self._build_event(client, timeline_name, name, start, end)

        if union:
            extra_criteria = {
                'timeline' : timeline_name,
                'name' : name
            }
            overlapping_activities = self.overlapping_dashes(client, start, end, **extra_criteria)

            if overlapping_activities:
                # consolidate all the overlapping activities into one
                # preserve the id of the first activity
                dash['_id'] = overlapping_activities[0]['_id']
                dash['start'] = min(start, *(a['start'] for a in overlapping_activities))
                dash['end'] = max(end, *(a['end'] for a in overlapping_activities))

                for a in overlapping_activities:
                    self.db.dashes.remove(a)

        self.db.dashes.save(dash)
        return dash

    def dashes(self, client, limit=10, **kwargs):
        '''Perform a general query for dashes. By default, will return all
           events unless filtering criteria are specified in kwargs.
           
           @param client : str
               the name of the client to which the event belongs
           @param limit : optional, int
                retrieve this many most-recent documents, defaults to 10
           @param kwargs : 
               mapping from keyword to list of values - valid keys are:

               name - the name of the event
               timeline - the name of the timeline'''

        criteria = {
            'client' : client
        }

        name = kwargs.get('name')
        if name:
            criteria['name'] = name

        timeline = kwargs.get('timeline')
        if timeline:
            criteria['timeline'] = timeline

        query = self.db.dashes.find(criteria)
        query = query.sort('end', -1)
        query = query.limit(limit)

        return tuple(query)[::-1]

    def overlapping_dashes(self, client, start, end, buffer_=None, **kwargs):
        '''Return timeline dashes that overlap with the time denoted by start
           and end
           
           @param client : str
               the name of the client to which the event belongs
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
            'client' : client,
            '$nor' : [
                { 'start' : { '$gt' : end } },
                { 'end' : { '$lt' : start } },
            ]
        })

        query = self.db.dashes.find(criteria)
        query = query.sort('end', 1)
        overlapping = tuple(query)

        return overlapping

    def pending(self, client, timeline_name, name, time=None):
        '''Log the beginning of a ranged activity to the specified timeline.

           @param client : str
               the name of the client to which the event belongs
           @param timeline_name : str
               name of the timeline
           @param name : str
               name of the activity
           @param time : optional, datetime
               the start/end time of the activity, defaults to now'''

        # look for an existing pending first
        pending = self.db.pendings.find_one({
            'client' : client,
            'timeline' : timeline_name,
            'name' : name,
        })

        if pending is not None:
            self.db.pendings.remove(pending)

            dash = self.dash(client, pending['timeline'], pending['name'], pending['start'], time)

            return dash

        else:

            if time is None:
                time = datetime.datetime.utcnow()

            pending = self._build_pending(client, timeline_name, name, time)
            self.db.pendings.insert(pending)

            return pending

    def cancel_pending(self, client, timeline_name, name):
        '''Cancel a pending that hasn't been completed yet.

           @param client : str
               the name of the client to which the event belongs
           @param timeline_name : str
               name of the timeline
           @param name : str
               name of the activity'''

        pending = self.db.pendings.find_one({
            'client' : client,
            'timeline' : timeline_name,
            'name' : name,
        })

        if pending is not None:
            self.db.pendings.remove(pending)

    def pendings(self, client, limit=10, **kwargs):
        '''Perform a general query for pendings. By default, will return all
           events unless filtering criteria are specified in kwargs.
           
           @param client : str
               the name of the client to which the event belongs
           @param limit : optional, int
                retrieve this many most-recent documents, defaults to 10
           @param kwargs : 
               mapping from keyword to list of values - valid keys are:

               name - the name of the event
               timeline - the name of the timeline'''

        criteria = {
            'client' : client
        }

        name = kwargs.get('name')
        if name:
            criteria['name'] = name

        timeline = kwargs.get('timeline')
        if timeline:
            criteria['timeline'] = timeline

        query = self.db.pendings.find(criteria)
        query = query.sort('start', -1)
        query = query.limit(limit)

        return tuple(query)[::-1]
