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

    def _build_dot(self, user, timeline_name, name, time, note=None):
        '''Helper function for building a dot object to be saved to the
           database.

           @param user : str
               the name of the user to which the event belongs
           @param timeline_name : str
               the name of the timeline to scan for overlapping activities
           @param name : str
               the name of the activity to create
           @param time : datetime
               the time of the dot, in UTC
           @param note : optional, str
               an optional note about the dot'''

        return dict(
            user=user,
            timeline=timeline_name,
            name=name,
            time=time,
            note=None
        )


    def _build_dash(self, user, timeline_name, name, start, end, note=None):
        '''Helper function for building an event object to be saved to the
           database.

           @param user : str
               the name of the user to which the event belongs
           @param timeline_name : str
               the name of the timeline to scan for overlapping activities
           @param name : str
               the name of the activity to create
           @param start : datetime
               the start time of the activity, in UTC
           @param end : datetime
               the end time of the activity, in UTC
           @param note : optional, str
               an optional note to attach to the dash'''

        data = dict(
            user=user,
            timeline=timeline_name,
            name=name,
            start=start,
            end=end,
            note=None
        )

        return data
    
    def _build_pending(self, user, timeline_name, name, start, note=None):
        '''Helper function for building a pending object to be saved to the 
           database.

           @param user : str
               the name of the user to which the event belongs
           @param timeline_name : str
               the name of the timeline to scan for overlapping activities
           @param name : str
               the name of the activity to create
           @param start : datetime
               the start time of the activity, in UTC
           @param note : optional, str
               an optional note to attach to the dash'''
        
        data = dict(
            user=user,
            timeline=timeline_name,
            name=name,
            start=start,
            note=None
        )

        return data

    def object_by_id(self, user, object_id, object_types=None):
        '''Get the object belonging to the specified user and having the 
           specified id.

           @param user : str
               the id of the user the object belongs to
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
            'user' : user,
        }

        for collection in object_types:
            obj = getattr(self.db, collection).find_one(criteria)

            if obj:
                return obj

    def user(self):
        '''Create a new user.'''

        user = dict()
        self.db.users.insert(user)
        return user

    def update_dot(self, user, dot):
        '''Update the dot in the database.

           @param user : str
               the user that owns the dot
           @param dot : dict
               the dot to update'''

        _id = dot.get('_id')

        if _id is None:
            raise ValueError('_id cannot be None')

        #TODO full validation of the dot object

        criteria = {
            '_id' : _id,
            'user' : user
        }

        dot = dict(dot)
        dot.pop('_id')
        self.db.dots.update(criteria, {'$set' : dot})

        return self.object_by_id(user, _id, 'dots')

    def dot(self, user, timeline_name, name, time=None, **kwargs):
        '''Log the occurence of an instaneous activity to the specified
           timeline.

           @param user : str
               the name of the user to which the event belongs
           @param timeline_name : str
               name of the timeline
           @param name : str
               name of the activity
           @param time : optional, datetime
               the time of the activity, defaults to now'''

        if time is None:
            time = datetime.datetime.utcnow()

        dot = self._build_dot(user, timeline_name, name, time, note=note)
        self.db.dots.insert(dot)
        
        return dot

    def dots(self, user, **kwargs):
        '''Perform a general query for dots. By default, will return all events 
           unless filtering criteria are specified in kwargs.
           
           @param user : str
               the id of the user to which the event belongs
           @param kwargs : 
               mapping from keyword to list of values - valid keys are:

               name - the name of the event
               timeline - the name of the timeline'''
        
        criteria = {
            'user' : user
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

    def overlapping_dots(self, user, start, end, buffer_=None, **kwargs):
        '''Return timeline dots that overlap with the time denoted by start
           and end
           
           @param user : str
               the name of the user to which the event belongs
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
            'user' : user,
            '$nor' : [
                { 'time' : { '$gt' : end } },
                { 'time' : { '$lt' : start } },
            ]
        })
        query = self.db.dots.find(criteria)
        query = query.sort('time', 1)
        overlapping = tuple(query)

        return overlapping

    def update_dash(self, user, dash):
        '''Update the dash in the database.

           @param user : str
               the user that owns the dash
           @param dash : dict
               the dash to update'''

        _id = dash.get('_id')

        if _id is None:
            raise ValueError('_id cannot be None')
            
        # TODO full validation of the dash object

        criteria = {
            '_id' : _id,
            'user' : user
        }

        dash = dict(dash)
        dash.pop('_id')
        self.db.dashes.update(criteria, {'$set' : dash})

        return self.object_by_id(user, _id, 'dashes')

    def dash(self, user, timeline_name, name, start=None, end=None, note=None):
        '''Log the occurence of a ranged activity to the specified timeline.

           @param user : str
               the name of the user to which the event belongs
           @param timeline_name : str
               name of the timeline
           @param name : str
               name of the activity
           @param start : optional, datetime
               the start time of the activity, defaults to now
           @param end : optional, datetime
               the end time of the activity, defaults to start
           @param note : optional, str
               an optional note to go with the dash'''

        if start is None:
            start = datetime.datetime.utcnow()

        if end is None:
            end = start

        dash = self._build_dash(user, timeline_name, name, start, end, note=note)

        extra_criteria = {
            'timeline' : timeline_name,
            'name' : name
        }
        overlapping_dashes = self.overlapping_dashes(user, start, end, **extra_criteria)

        if overlapping_dashes:
            # consolidate all the overlapping activities into one
            # preserve the id of the first activity
            dash['_id'] = overlapping_dashes[0]['_id']
            dash['start'] = min(start, *(a['start'] for a in overlapping_dashes))
            dash['end'] = max(end, *(a['end'] for a in overlapping_dashes))

            # concatenate all of the non None notes
            notes = list()
            if note:
                notes.append(note)

            for a in overlapping_dashes:
                _note = a.get('note')
                if _note:
                    notes.append(_note)
                self.db.dashes.remove(a)

            if notes:
                dash['note'] = '\n\n'.join(notes)

        self.db.dashes.save(dash)
        return dash

    def dashes(self, user, **kwargs):
        '''Perform a general query for dashes. By default, will return all
           events unless filtering criteria are specified in kwargs.
           
           @param user : str
               the name of the user to which the event belongs
           @param kwargs : 
               mapping from keyword to list of values - valid keys are:

               name - the name of the event
               timeline - the name of the timeline'''

        criteria = {
            'user' : user
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

    def overlapping_dashes(self, user, start, end, buffer_=None, **kwargs):
        '''Return timeline dashes that overlap with the time denoted by start
           and end
           
           @param user : str
               the name of the user to which the event belongs
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
            'user' : user,
            '$nor' : [
                { 'start' : { '$gt' : end } },
                { 'end' : { '$lt' : start } },
            ]
        })

        query = self.db.dashes.find(criteria)
        query = query.sort('end', 1)
        overlapping = tuple(query)

        return overlapping

    def update_pending(self, user, pending):
        '''Update the pending to the database.

           @param user : str
               the user that owns the pending
           @param pending : dict
               the pending to update'''

        _id = pending.get('_id')

        if _id is None:
            raise ValueError('_id cannot be None')

        #TODO full validation of the pending object

        criteria = {
            '_id' : _id,
            'user' : user
        }

        pending = dict(pending)
        pending.pop('_id')
        self.db.pendings.update(criteria, {'$set' : pending})

        return self.object_by_id(user, _id, 'pendings')

    def pending(self, user, timeline_name, name, time=None, note=None):
        '''Log the beginning of a ranged activity to the specified timeline.

           @param user : str
               the name of the user to which the event belongs
           @param timeline_name : str
               name of the timeline
           @param name : str
               name of the activity
           @param time : optional, datetime
               the start/end time of the activity, defaults to now
           @param note : optional, str
               an optional note to attach to the pending'''

        # look for an existing pending first
        pending = self.db.pendings.find_one({
            'user' : user,
            'timeline' : timeline_name,
            'name' : name,
        })

        if pending is not None:
            self.db.pendings.remove(pending)

            dash = self.dash(user, pending['timeline'], pending['name'], pending['start'], time)

            return dash

        else:

            if time is None:
                time = datetime.datetime.utcnow()

            pending = self._build_pending(user, timeline_name, name, time, note=note)
            self.db.pendings.insert(pending)

            return pending

    def cancel_pending(self, user, timeline_name, name):
        '''Cancel a pending that hasn't been completed yet.

           @param user : str
               the name of the user to which the event belongs
           @param timeline_name : str
               name of the timeline
           @param name : str
               name of the activity'''

        pending = self.db.pendings.find_one({
            'user' : user,
            'timeline' : timeline_name,
            'name' : name,
        })

        if pending is not None:
            self.db.pendings.remove(pending)

    def pendings(self, user, **kwargs):
        '''Perform a general query for pendings. By default, will return all
           events unless filtering criteria are specified in kwargs.
           
           @param user : str
               the name of the user to which the event belongs
           @param kwargs : 
               mapping from keyword to list of values - valid keys are:

               name - the name of the event
               timeline - the name of the timeline'''

        criteria = {
            'user' : user
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

    def search(self, user, search_dots=True, search_dashes=True, search_pendings=True, **kwargs):
        '''Search through the database for events that match the criteria.

           @param user : str
               the name of the user whose events will be searched
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
            dots = self.dots(user, **kwargs)
            data['dots'] = dots

        if search_dashes:
            dashes = self.dashes(user, **kwargs)
            data['dashes'] = dashes
        
        if search_pendings:
            pendings = self.pendings(user, **kwargs)
            data['pendings'] = pendings

        return data

