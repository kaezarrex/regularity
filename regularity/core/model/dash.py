import pymongo.objectid

from regularity.core.validation import DateTimeField, StringField, Validator

from base import APIBase, validate
from fields import ObjectIdField

class Dash(Validator):
    '''The validator for dash objects'''

    _id      = ObjectIdField()
    user     = StringField()
    timeline = StringField(null=True)
    name     = StringField()
    start    = DateTimeField()
    end      = DateTimeField()
    note     = StringField(null=True)

class DashAPI(object):

    CONTIGUITY_THRESHOLD = 5 # seconds

    @property
    def collection(self):
        '''Return the database collection for this API'''

        return self.db.dashes

    def create(self, user, timeline, name, start=None, end=None, note=None):
        '''Log the occurence of a ranged activity to the specified timeline.

           @param user : str|pymongo.objectid.ObjectId
               the name of the user to which the event belongs
           @param timeline: str
               name of the timeline
           @param name : str
               name of the activity
           @param start : optional, datetime
               the start time of the activity, defaults to now
           @param end : optional, datetime
               the end time of the activity, defaults to start
           @param note : optional, str
               an optional note to go with the dash'''

        user = self.object_id(user)

        if start is None:
            start = datetime.datetime.utcnow()

        if end is None:
            end = start

        dash = dict(
            _id=pymongo.objectid.ObjectId(),
            user=user,
            timeline=timeline,
            name=name,
            start=start,
            end=end,
            note=note,
        )

        extra_criteria = {
            'timeline' : timeline,
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
                self.collection.remove(a)

            if notes:
                dash['note'] = '\n\n'.join(notes)

        self.collection.save(dash)
        return dash

    @validate(Dash)
    def update(self, dash):
        '''Update the dash in the database.

           @param dash : dict
               the dash to update'''

        self.verify(dash)

        self.collection.save(dash)
        return dash

    @validate(Dash)
    def delete_dash(self, dash):
        '''Delete the dash with object_id that belongs to the user.

           @param dash : dict
               the dash to delete'''

        dash = self.verify(dash)

        if dash:
            self.collection.remove(dash)

    def overlapping_dashes(self, user, start, end, buffer_=None, **kwargs):
        '''Return timeline dashes that overlap with the time denoted by start
           and end
           
           @param user : str|pymongo.objectid.ObjectId
               the id of the user to which the event belongs
           @param start : datetime
               the start time of the activity
           @param end : datetime
               the end time of the activity
           @param buffer : optional, int
               the number of seconds to buffer out the time range, useful for 
               catching events that barely don't overlap, defaults to 5 seconds
           @param kwargs : optional
               additional criteria for the query'''

        user = self.object_id(user)

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

        query = self.collection.find(criteria)
        query = query.sort('end', 1)
        overlapping = tuple(query)

        return overlapping

    def search(self, user, **kwargs):
        '''Perform a general query for dashes. By default, will return all
           events unless filtering criteria are specified in kwargs.
           
           @param user : str|pymongo.objectid.ObjectId
               the id of the user to which the event belongs
           @param kwargs : 
               mapping from keyword to list of values - valid keys are:

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
        query = query.sort('end', 1)

        return tuple(query)
