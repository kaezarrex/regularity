
import datetime as _datetime

from pymongo.objectid import ObjectId

from regularity.core.recurse import recurse

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

def serialize(o, **kwargs):
    '''(De)serialize the object with the serializers passed in as keyword
       arguments. The object may an arbitrary nesting of dicts/lists, however
       see regularity.utils.recurse() for the assumptions that are made about
       the data.

       @param o : dict | iterable
           the object to serialize
       @param kwargs : keyword arguments
           a mapping of field name -> serializer function'''

    def callback(key, value):
        if key in kwargs:
            function = kwargs[key]
            return function(value)

    return recurse(o, callback)
    
_int = int
def int(o):
    '''(De)serialize the object to/from int/str.

       @param o : int | str
           the object to (de)serialize'''

    if isinstance(o, basestring):
        return _int(o)
    elif isinstance(o, _int):
        str(o)

def object_id(o):
    '''(De)serialize the object to/from ObjectID/str.

       @param o : pymongo.objectid.ObjectId | str
           the object to (de)serialize'''

    if isinstance(o, basestring):
        # deserialize to datetime
        return ObjectId(o)

    elif isinstance(o, ObjectId):
        # serialize to string
        return str(o)

    raise ValueError('%s is not a string or datetime' % o)

def datetime(o):
    '''(De)serialize the object to/from datetime/str.

       @param o : datetime | str
           the object to (de)serialize'''

    if isinstance(o, basestring):
        # deserialize to datetime
        return _datetime.datetime.strptime(o, DATETIME_FORMAT)

    elif isinstance(o, _datetime.datetime):
        # serialize to string
        return o.strftime(DATETIME_FORMAT)

    raise ValueError('%s is not a string or datetime' % o)
