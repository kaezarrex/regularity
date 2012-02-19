import pymongo.objectid

from regularity.core.validation import DateTimeField, StringField, Validator

from base import APIBase, validate
from fields import ObjectIdField

class Pending(Validator):

    _id      = ObjectIdField()
    user     = StringField()
    timeline = StringField(null=True)
    name     = StringField()
    start    = DateTimeField()
    note     = StringField(null=True)

class DotAPI(object):

    @property
    def collection(self):
        '''Return the database collection for this API'''

        return self.db.pendings

    def create(self, user, timeline, name, time=None, note=None):
        '''Log the beginning of a ranged activity, where the end time is yet to
           be determined, to the specified timeline.

           @param user : str|pymongo.objectid.ObjectId
               the name of the user to which the event belongs
           @param timeline : str
               name of the timeline
           @param name : str
               name of the activity
           @param time : optional, datetime
               the start time of the activity, defaults to now
           @param note : optional, str
               an optional note to attach to the pending'''

        user = self.object_id(user)

        if time is None:
            time = datetime.datetime.utcnow()

        pending = dict(
            user=user,
            timeline=timeline,
            name=name,
            start=start,
            note=note,
        )

        self.collection.insert(pending)

        return pending

    @validate(Pending)
    def update(self, pending):
        '''Update the pending to the database.

           @param pending : dict
               the pending to update'''

        self.verify(pending)

        self.collection.save(pending)
        return pending

    @validate(Pending)
    def delete(self, pending):
        '''Cancel a pending that hasn't been completed yet.

           @param pending : dict
               the pending to delete'''

        pending = self.verify(pending)

        if pending:
            self.collection.remove(pending)

    def search(self, user, **kwargs):
        '''Perform a general query for pendings. By default, will return all
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
        query = query.sort('start', 1)

        return tuple(query)


