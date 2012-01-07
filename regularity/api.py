import httplib
import json
import urllib

import requests

from regularity import serializers

def require_client(func):
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'client') or self.client is None:
            raise BaseException('client must be set for this call.')

        return func(self, *args, **kwargs)
    return wrapper

def post(url, data=None, serializers=None):
    '''Simple function for making a POST request and handling different status
       codes.

       @param url : str
           the url to hit
       @param data : optional, dict
           the data to include
       @param serializers : dict
           a mapping of serializer functions for any fields that need so'''

    # serialize any fields that need so
    if serializers:
        for key, fn in serializers.iteritems():
            data[key] = fn(data[key])

    response = requests.post(url, data=data)

    if 200 == response.status_code:
        data = response.content
        data = json.loads(data)

        # deserialize any fields that need so
        if serializers:
            for key, fn in serializers.iteritems():
                data[key] = fn(data[key])

        return data
    else:
        return None
    

class API(object):

    def __init__(self, host, port, client=None):
        self.base_url = 'http://%s:%d' % (host, port)
        self.client = client

    def url(self, path):
        return '%s%s' % (self.base_url, path)

    def init(self):
        url = self.url('/client/create')

        data = post(url)

        return data
    
    @require_client
    def dot(self, timeline, activity, time): 
        url = self.url('/client/%s/dot' % self.client)

        data = dict(
            timeline=timeline,
            activity=activity,
            time=time
        )

        data = post(url, data=data, serializers=dict(
            time=serializers.datetime
        ))

        return data
    
    @require_client
    def dash(self, timeline, activity, start, end): 
        url = self.url('/client/%s/dash' % self.client)

        data = dict(
            timeline=timeline,
            activity=activity,
            start=start,
            end=end
        )

        data = post(url, data=data, serializers=dict(
            start=serializers.datetime,
            end=serializers.datetime
        ))

        return data

