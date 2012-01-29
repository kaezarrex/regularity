import json
import urlparse

import web

import serializers
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
                else:
                    data[key] = value

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
        client = model.client()
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

        dot = model.dot(client, timeline, activity, time)
        dot['_id'] = str(dot['_id'])

        return data

class DashAPI(object):

    @encode_json(start=serializers.datetime, end=serializers.datetime)
    def POST(self, client, data):
        timeline = data['timeline']
        activity = data['activity']
        start = data['start']
        end = data['end']

        data = model.dash(client, timeline, activity, start, end)
        data['_id'] = str(data['_id'])

        return data

class DeferAPI(object):

    @encode_json(start=serializers.datetime)
    def POST(self, client, data):
        timeline = data['timeline']
        activity = data['activity']
        start = data['start']
        
        data = model.defer(client, timeline, activity, start)
        data['_id'] = str(data['_id'])

        return data


