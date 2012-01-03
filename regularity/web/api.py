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
        data = web.data()
        data = urlparse.parse_qs(data)
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

