import json
import urlparse

import web

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
        _id = str(client['_id'])

        return dict(
            client=_id
        )

class DotAPI(object):

    @encode_json
    @parse_data
    def POST(self, client, data):
        print data

        return dict(_id='test id')
