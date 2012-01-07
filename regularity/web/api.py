import json
import urlparse

import web

from regularity import serializers
from regularity.model import Model
model = Model()

def encode_json(func):
    def wrapper(*args, **kwargs):
        web.header('Content-Type', 'application/json')
        data = func(*args, **kwargs)
        return json.dumps(data)
    return wrapper

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

    @encode_json
    @parse_data
    def POST(self, data):
        client = model.create_client()
        data['_id'] = str(data['_id'])

        return dict(
            client=_id
        )

class DotAPI(object):

    @encode_json
    @parse_data
    def POST(self, client, data):
        time = serializers.datetime(data['time'])

        _data = model.log(client, data['timeline'], data['activity'], time, time)
        
        data = dict()
        data['_id'] = str(_data['_id'])
        data['time'] = serializers.datetime(_data['start'])

        return data

class DashAPI(object):

    @encode_json
    @parse_data
    def POST(self, client, data):
        start = serializers.datetime(data['start'])
        end = serializers.datetime(data['end'])

        data = model.log(client, data['timeline'], data['activity'], start, end)
        data['_id'] = str(data['_id'])
        data['start'] = serializers.datetime(data['start'])
        data['end'] = serializers.datetime(data['end'])

        return data
