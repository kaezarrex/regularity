
import datetime as _datetime

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
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

    else:
        raise ValueError('%s is not a string or datetime' % o)
