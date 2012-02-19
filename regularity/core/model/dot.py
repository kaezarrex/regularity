import datetime
import re

import pymongo.objectid

from regularity.core.validation import DateTimeField, StringField, Validator

from base import APIBase, validate
from fields import ObjectIdField

class DotValidator(Validator):
    '''The validator for dot objects'''

    _id      = ObjectIdField()
    user     = ObjectIdField()
    timeline = StringField(null=True)
    name     = StringField()
    time     = DateTimeField()
    note     = StringField(null=True)

class DotAPI(APIBase):

    @property
    def collection(self):
        '''Return the database collection for this API'''

        return self.db.dots

    def create(self, user, timeline, name, time=None, note=None):
        '''Log the occurence of an instantaneous activity to the specified
           timeline.

           @param user : str|pymongo.objectid.ObjectId
               the name of the user to which the event belongs
           @param timeline : str
               name of the timeline
           @param name : str
               name of the activity
           @param time : optional, datetime
               the time of the activity, defaults to now
           @param note : optional, str
               a note to attach to the dot'''

        user = self.object_id(user)

        if time is None:
            time = datetime.datetime.utcnow()

        dot = dict(
            _id=pymongo.objectid.ObjectId(),
            user=user, 
            timeline=timeline, 
            name=name, 
            time=time, 
            note=note
        )
        dot = DotValidator.validate(dot)

        self.collection.insert(dot)
        
        return dot

    @validate(DotValidator)
    def update(self, dot):
        '''Update the dot in the database. 
        
           Raises ItemNotFound if the item does not exist.

           @param dot : dict
               the dot to update'''

        self.verify(dot)

        self.collection.save(dot)
        return dot

    @validate(DotValidator)
    def delete(self, dot):
        '''Delete the dot in the database.

           Raises ItemNotFound if the item does not exist.

           @param dot : dict
               the dot to be deleted'''

        dot = self.verify(dot)

        if dot:
            self.collection.remove(dot)

    def overlapping(self, user, start, end, buffer_=None, **kwargs):
        '''Return dots that overlap with the time denoted by start and end.
           
           @param user : str|pymongo.objectid.ObjectId
               the id of the user to which the event belongs
           @param start : datetime
               the start time of the range
           @param end : datetime
               the end time of the range
           @param buffer : optional, int
               the number of seconds to buffer out the time range, useful for 
               catching events that barely don't overlap, defaults to 5 seconds
           @param kwargs : optional
               additional filtering criteria for the query'''

        user = self.object_id(user)

        if buffer_ is not None:
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

        query = self.collection.find(criteria)
        query = query.sort('time', 1)
        
        return tuple(query)

    def search(self, user, **kwargs):
        '''Perform a general query for dots. By default, will return all events 
           unless filtering criteria are specified in kwargs.
           
           @param user : str|pymongo.objectid.ObjectId
               the id of the user to which the event belongs
           @param kwargs : 
               additional filtering criteria - valid keys are:

               name - the name of the event
               timeline - the name of the timeline'''
        
        user = self.object_id(user)
        criteria = {
            'user' : user
        }

        name = kwargs.get('name')
        if name:
            criteria['name'] = re.compile(re.escape(name), re.IGNORECASE)

        timeline = kwargs.get('timeline')
        if timeline:
            criteria['timeline'] = timeline

        query = self.collection.find(criteria)
        query = query.sort('time', 1)

        return tuple(query)

