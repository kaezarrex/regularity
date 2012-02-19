
class ItemNotFound(Exception):
    '''An exception for when a requested database item does not exist'''

    def __init__(item):
        '''Create the ItemNotFound exception.

           @param item : dict
               the item that could not be found in the database'''

        super(ItemNotFound, self).__init__()
        self.item = item

def validate(validator):
    '''Create a decorator that will validate data coming in before the decorated
       function gets called. A ValidationError will be thrown in the data does
       not validate.

       @param validator : regularity.core.validation.Validator
           the validator to use'''

    def decorator(fn):
        def wrapper(self, data):
            data = validator.validate(data)
            return self.fn(data)

        return wrapper

    return decorator

class APIBase(object):

    def __init__(self, db):
        '''Create an APIBase object.

           @param connection : pymongo.Connection
               the connection to the database'''

        self.db = db

    def object_id(self, value):
        '''Convert the value into a pymongo.objectid.ObjectId.

           @param value : str|pymongo.objectid.ObjectId
               the value to convert'''

        return pymongo.objectid.ObjectId(value)

    @property
    def collection(self):
        '''Meant for subclasses to implement - returns the collection that the
           subclass is managing.'''

        raise NotImplementedError('collection() must be defined in subclasses')

    def verify(self, item):
        '''Verify the item exists and belongs to the user it says it does. Will
           raise ItemNotFound if the item does not exist.

           @param item : dict
               an object claiming to be a document in the database'''

        _id = item.get('_id')
        user = item('user')

        obj = self.object_by_id(user, _id) 
        
        if obj is None:
            raise ItemNotFound(item)

        return obj

    def object_by_id(self, user, object_id):
        '''Get the object belonging to the specified user and having the 
           specified id.

           @param user : str
               the id of the user the object belongs to
           @param object_id : pymongo.objectid.ObjectId
               the id of the object'''

        criteria = {
            '_id' : object_id,
            'user' : user,
        }

        return self.collection.find_one(criteria)

