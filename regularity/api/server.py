import json
import urlparse

import web

import serializers

# this will be populated by the main executable
model = None

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

            # assume that the function returns a dict or iterable - if it is an
            # iterable, assume each object in it is a dict
            data = serializers.serialize(data, **_serializers)

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

    @encode_json(_id=serializers.object_id, time=serializers.datetime)
    def GET(self, client, data):
        dots = model.dots(client)

        return dots

    @encode_json(_id=serializers.object_id, time=serializers.datetime)
    def POST(self, client, data):
        timeline = data['timeline']
        activity = data['activity']
        time = data['time']

        dot = model.dot(client, timeline, activity, time)

        return dot

class DashAPI(object):

    @encode_json(_id=serializers.object_id, start=serializers.datetime, end=serializers.datetime)
    def GET(self, client, data):
        dashes = model.dashes(client)

        return dashes


    @encode_json(_id=serializers.object_id, start=serializers.datetime, end=serializers.datetime)
    def POST(self, client, data):
        timeline = data['timeline']
        activity = data['activity']
        start = data['start']
        end = data['end']

        dash = model.dash(client, timeline, activity, start, end)

        return dash

class PendingAPI(object):

    @encode_json(_id=serializers.object_id, start=serializers.datetime)
    def GET(self, client, data):
        pendings = model.pendings(client)

        return pendings

    @encode_json(_id=serializers.object_id, start=serializers.datetime, end=serializers.datetime)
    def POST(self, client, data):
        timeline = data['timeline']
        activity = data['activity']
        start = data['start']
        
        pending = model.pending(client, timeline, activity, start)

        return pending


