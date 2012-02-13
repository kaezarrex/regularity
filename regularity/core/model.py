import datetime
import re

import pymongo
import pymongo.objectid

class RegularityValidationError(Exception):
    '''An exception due to one or more fields not validating.'''

    def __init__(self, **kwargs):
        '''Create the exception.

           @param kwargs : keyword arguments
               the fields that did not validate - this is a mapping from field
               -> error message'''

        super(RegularityValidationError, self).__init__()
        self.fields = fields

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

    def object_by_id(self, client, object_id, object_types=None):
        '''Get the object belonging to the specified client and having the 
           specified id.

           @param client : str
               the id of the client the object belongs to
           @param object_id : str|pymongo.objectid.ObjectId
               the id of the object
           @param object_types : optional, str|list(str)|tuple(str)
               the type of objects to search - if None, then every collection 
               will be searched, otherwise only the specified collection will 
               be searched - valid values are 'dots', 'dashs', 'pendings'.'''

        if isinstance(object_id, basestring):
            object_id = pymongo.objectid.ObjectId(object_id)

        if object_types is None:
            object_types = ('dots', 'dashes', 'pendings')
        elif isinstance(object_types, basestring):
            object_types = (object_types,)

        criteria = {
            '_id' : object_id,
            'client' : client,
        }

        for collection in object_types:
            obj = getattr(self.db, collection).find_one(criteria)

            if obj:
                return obj

    def client(self):
        '''Create a new client.'''

        client = dict()
        self.db.clients.insert(client)
        return client

    def update_dot(self, client, dot):
        '''Update the dot in the database.

           @param client : str
               the client that owns the dot
           @param dot : dict
               the dot to update'''

        _id = dot.get('_id')

        if _id is None:
            raise ValueError('_id cannot be None')

        #TODO full validation of the dot object

        criteria = {
            '_id' : _id,
            'client' : client
        }

        dot = dict(dot)
        dot.pop('_id')
        self.db.dots.update(criteria, {'$set' : dot})

        return self.object_by_id(client, _id, 'dots')

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

    def dots(self, client, **kwargs):
        '''Perform a general query for dots. By default, will return all events 
           unless filtering criteria are specified in kwargs.
           
           @param client : str
               the id of the client to which the event belongs
           @param kwargs : 
               mapping from keyword to list of values - valid keys are:

               name - the name of the event
               timeline - the name of the timeline'''

        criteria = {
            'client' : client
        }

        name = kwargs.get('name')
        if name:
            criteria['name'] = re.compile(re.escape(name), re.IGNORECASE)

        timeline = kwargs.get('timeline')
        if timeline:
            criteria['timeline'] = timeline

        query = self.db.dots.find(criteria)
        query = query.sort('time', 1)

        return tuple(query)

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

    def update_dash(self, client, dash):
        '''Update the dash in the database.

           @param client : str
               the client that owns the dash
           @param dash : dict
               the dash to update'''

        _id = dash.get('_id')

        if _id is None:
            raise ValueError('_id cannot be None')
            
        # TODO full validation of the dash object

        criteria = {
            '_id' : _id,
            'client' : client
        }

        dash = dict(dash)
        dash.pop('_id')
        self.db.dashes.update(criteria, {'$set' : dash})

        return self.object_by_id(client, _id, 'dashes')

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

    def dashes(self, client, **kwargs):
        '''Perform a general query for dashes. By default, will return all
           events unless filtering criteria are specified in kwargs.
           
           @param client : str
               the name of the client to which the event belongs
           @param kwargs : 
               mapping from keyword to list of values - valid keys are:

               name - the name of the event
               timeline - the name of the timeline'''

        criteria = {
            'client' : client
        }

        name = kwargs.get('name')
        if name:
            criteria['name'] = re.compile(re.escape(name), re.IGNORECASE)

        timeline = kwargs.get('timeline')
        if timeline:
            criteria['timeline'] = timeline

        query = self.db.dashes.find(criteria)
        query = query.sort('end', 1)

        return tuple(query)

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

    def update_pending(self, client, pending):
        '''Update the pending to the database.

           @param client : str
               the client that owns the pending
           @param pending : dict
               the pending to update'''

        _id = pending.get('_id')

        if _id is None:
            raise ValueError('_id cannot be None')

        #TODO full validation of the pending object

        criteria = {
            '_id' : _id,
            'client' : client
        }

        pending = dict(pending)
        pending.pop('_id')
        self.db.pendings.update(criteria, {'$set' : pending})

        return self.object_by_id(client, _id, 'pendings')

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

    def pendings(self, client, **kwargs):
        '''Perform a general query for pendings. By default, will return all
           events unless filtering criteria are specified in kwargs.
           
           @param client : str
               the name of the client to which the event belongs
           @param kwargs : 
               mapping from keyword to list of values - valid keys are:

               name - the name of the event
               timeline - the name of the timeline'''

        criteria = {
            'client' : client
        }

        name = kwargs.get('name')
        if name:
            criteria['name'] = re.compile(re.escape(name), re.IGNORECASE)

        timeline = kwargs.get('timeline')
        if timeline:
            criteria['timeline'] = timeline

        query = self.db.pendings.find(criteria)
        query = query.sort('start', 1)

        return tuple(query)

    def search(self, client, search_dots=True, search_dashes=True, search_pendings=True, **kwargs):
        '''Search through the database for events that match the criteria.

           @param client : str
               the name of the client whose events will be searched
           @param search_dots : optional, bool
               a flag controlling whether dots are searched
           @param search_dashes : optional, bool
               a flag controlling whether dashes are searched
           @param search_pendings : optional, bool
               a flag controlling whether pendings are searched
           @param kwargs : keyword arguments
               search criteria for the events to find:
               
               name : str
                   the name of the events to look for'''

        data = dict()

        if search_dots:
            dots = self.dots(client, **kwargs)
            data['dots'] = dots

        if search_dashes:
            dashes = self.dashes(client, **kwargs)
            data['dashes'] = dashes
        
        if search_pendings:
            pendings = self.pendings(client, **kwargs)
            data['pendings'] = pendings

        return data

