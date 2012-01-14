import json
import urlparse

import web

from regularity import serializers
from regularity.model import Model
model = Model()

# TODO make this decorator handle the input and output of the functions it decorates
#   ie, absorb the functionality of parse_data
def encode_json(**kwargs):
    '''Create a decorator for a function that encodes its return value as JSON.

       @param kwargs : dict
           a mapping of key value to serializer, in case the value is not
           JSON serializable by default'''

    _serializers = kwargs

    def decorator(func):
        def wrapper(*args, **kwargs):
            web.header('Content-Type', 'application/json')
            data = func(*args, **kwargs)

            # perform any serializations
            if isinstance(data, dict):
                for key, value in data.iteritems():
                    if key in _serializers:
                        data[key] = _serializers[key](value)


            return json.dumps(data)
        return wrapper
    return decorator

def parse_data(func):
    def wrapper(*args, **kwargs):
        _data = web.data()
        _data = urlparse.parse_qs(_data)

        data = dict()
        for k, v in _data.iteritems():
            if not isinstance(v, list):
                data[k] = v
            
            if 1 == len(v):
                data[k] = v[0]
            else:
                raise BaseException('key %s in query must not be supplied multiple times' % k)

        args = args + (data,)
        return func(*args, **kwargs)
    return wrapper

class ClientAPI(object):

    @encode_json()
    @parse_data
    def POST(self, data):
        client = model.create_client()
        data['_id'] = str(data['_id'])

        return dict(
            client=_id
        )

class DotAPI(object):

    @encode_json(time=serializers.datetime)
    @parse_data
    def POST(self, client, data):
        time = serializers.datetime(data['time'])

        _data = model.log(client, data['timeline'], data['activity'], time, time)
        
        data = dict()
        data['_id'] = str(_data['_id'])
        data['time'] = _data['start']

        return data

class DashAPI(object):

    @encode_json(start=serializers.datetime, end=serializers.datetime)
    @parse_data
    def POST(self, client, data):
        start = serializers.datetime(data['start'])
        end = serializers.datetime(data['end'])

        data = model.log(client, data['timeline'], data['activity'], start, end)
        data['_id'] = str(data['_id'])

        return data
