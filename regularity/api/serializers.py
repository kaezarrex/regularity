
import datetime as _datetime

from pymongo.objectid import ObjectId

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

def serialize_dict(data, **kwargs):
    '''(De)Serialize the values in the dictionary, using the serializers passed
       in as keyword arguments.

       @param d : dict
           the dictionary whose values are to be transformed
       @param kwargs : keyword arguments
           serializers to use'''

    new_data = dict()
    for key, value in data.iteritems():
        if key in kwargs:
            new_data[key] = kwargs[key](value)
        else:
            new_data[key] = value

    return new_data

def serialize(o, **kwargs):
    '''(De)serialize the object with the serializers passed in as keyword
       arguments. The object may be a dict, or an iterable of dicts.

       @param o : dict | iterable
           the object to serialize
       @param kwargs : keyword arguments
           serializers to use'''

    if o is None:
        return None
    elif isinstance(o, dict):
        return serialize_dict(o, **kwargs)
    elif hasattr(o, '__iter__'):
        return tuple(serialize_dict(d, **kwargs) for d in o)

    raise BaseException('object is not list or iterable')

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
