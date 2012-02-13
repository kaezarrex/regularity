import json
import logging
import os
import sys
import urlparse

import web

from regularity.core import serializers
from regularity.core.model import Model

config_path = os.environ.get('REGULARITY_API_CONFIG')
if config_path is None:
    logging.critical('no config specified!')
    sys.exit(1)

with open(config_path, 'r') as config_file:
    try:
        config = json.load(config_file)

        db = config['db']

    except (Exception, BaseException) as e:
        logging.critical(str(e))
        raise e

    model = Model(
        host=db['host'],
        port=db['port'],
        user=db['user'],
        password=db['password'],
        database=db['database'],
    )
    model = model


def encode_json(**kwargs):
    '''Create a decorator for a function that encodes its return value as JSON.

       @param kwargs : dict
           a mapping of key value to serializer, in case the value is not
           JSON serializable by default'''

    _serializers = kwargs

    def decorator(func):
        def wrapper(*args, **kwargs):
            data = dict(web.input())

            data = serializers.serialize(data, **_serializers)

            kwargs.update(data)
            data = func(*args, **kwargs)

            if data is not None:
                data = serializers.serialize(data, **_serializers)
                return json.dumps(data)

            web.header('Content-Type', 'application/json')
            
        return wrapper
    return decorator

class ClientAPI(object):

    @encode_json(**{
        '_id' : serializers.object_id
    })
    def POST(self):
        client = model.client()

        return client

class DotAPI(object):

    @encode_json(**{
        'limit' : serializers.int, 
        '_id' : serializers.object_id, 
        'time' : serializers.datetime
    })
    def GET(self, client, name=None, limit=10):
        dots = model.dots(client, name=name)

        return dots[-limit:]

    @encode_json(**{
        '_id' : serializers.object_id, 
        'time' : serializers.datetime,
    })
    def POST(self, client, **kwargs):
        timeline = kwargs['timeline']
        activity = kwargs['activity']
        time = kwargs['time']

        dot = model.dot(client, timeline, activity, time)

        return dot

class DashAPI(object):

    @encode_json(**{
        'limit' : serializers.int, 
        '_id' : serializers.object_id, 
        'start' : serializers.datetime, 
        'end' : serializers.datetime
    })
    def GET(self, client, name=None, limit=10):
        dashes = model.dashes(client, name=name)

        return dashes[-limit:]


    @encode_json(**{
        '_id' : serializers.object_id, 
        'start' : serializers.datetime, 
        'end' : serializers.datetime
    })
    def POST(self, client, **kwargs):
        timeline = kwargs['timeline']
        activity = kwargs['activity']
        start = kwargs['start']
        end = kwargs['end']

        dash = model.dash(client, timeline, activity, start, end)

        return dash

class PendingAPI(object):

    @encode_json(**{
        'limit' : serializers.int, 
        '_id' : serializers.object_id, 
        'start' : serializers.datetime
    })
    def GET(self, client, name=None, limit=10):
        pendings = model.pendings(client, name=name)

        return pendings[-limit:]

    @encode_json(**{
        '_id' : serializers.object_id, 
        'start' : serializers.datetime, 
        'end' : serializers.datetime
    })
    def POST(self, client, **kwargs):
        timeline = kwargs['timeline']
        activity = kwargs['activity']
        start = kwargs['start']
        
        pending = model.pending(client, timeline, activity, start)

        return pending

class PendingInstanceAPI(object):

    @encode_json()
    def DELETE(self, client, timeline, activity):

        model.cancel_pending(client, timeline, activity)


