import json

import web

from regularity.model import Model
model = Model()

def content_type(content_type):
    def decorator(func):
        def wrapper(*args, **kwargs):
            web.header('Content-Type', content_type)
            return func(*args, **kwargs)
        return wrapper
    return decorator

JSON_CONTENT_TYPE = 'application/json'

class ClientAPI(object):

    @content_type(JSON_CONTENT_TYPE)
    def POST(self):
        client = model.create_client()
        _id = str(client['_id'])

        return json.dumps(dict(
            client=_id
        ))

