import json
import urlparse

import web

from regularity import serializers
from regularity.model import Model
model = Model()

def encode_json(**kwargs):
    '''Create a decorator for a function that encodes its return value as JSON.

       @param kwargs : dict
           a mapping of key value to serializer, in case the value is not
           JSON serializable by default'''

    _serializers = kwargs

    def decorator(func):
        def wrapper(*args, **kwargs):
            data = web.data()
            data = urlparse.parse_qs(data)

            for key, value in data.iteritems():
                if not value:
                    continue

                value = value[0]
                if key in _serializers:
                    data[key] = _serializers[key](value)

            args = args + (data,)
            data = func(*args, **kwargs)

            # assume that the function returns a dict
            for key, value in data.iteritems():
                if key in _serializers:
                    data[key] = _serializers[key](value)


            web.header('Content-Type', 'application/json')
            return json.dumps(data)
        return wrapper
    return decorator

class ClientAPI(object):

    @encode_json()
    def POST(self, data):
        client = model.create_client()
        data['_id'] = str(data['_id'])

        return dict(
            client=_id
        )

class DotAPI(object):

    @encode_json(time=serializers.datetime)
    def POST(self, client, data):
        timeline = data['timeline']
        activity = data['activity']
        time = data['time']

        _data = model.log(client, timeline, activity, time, time)
        
        data = dict()
        data['_id'] = str(_data['_id'])
        data['time'] = _data['start']

        return data

class DashAPI(object):

    @encode_json(start=serializers.datetime, end=serializers.datetime)
    def POST(self, client, data):
        timeline = data['timeline']
        activity = data['activity']
        start = data['start']
        end = data['end']

        data = model.log(client, timeline, activity, start, end)
        data['_id'] = str(data['_id'])

        return data

