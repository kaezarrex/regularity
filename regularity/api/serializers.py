
import datetime as _datetime

from pymongo.objectid import ObjectId

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

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
