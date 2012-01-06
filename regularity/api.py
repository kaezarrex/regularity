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

class API(object):

    def __init__(self, host, port, client=None):
        self.base_url = 'http://%s:%d' % (host, port)
        self.client = client

    def url(self, path):
        return '%s%s' % (self.base_url, path)

    def init(self):
        url = self.url('/client/create')
        response = requests.post(url)

        if 200 == response.status_code:
            data = response.content
            data = json.loads(data)
            return data
    
    @require_client
    def dot(self, timeline, activity, time): 
        url = self.url('/client/%s/dot' % self.client)

        time = serializers.datetime(time)
        data = dict(
            timeline=timeline,
            activity=activity,
            time=time
        )

        response = requests.post(url, data=data)

        if 200 == response.status_code:
            data = response.content
            data = json.loads(data)
            return data
    
    @require_client
    def dash(self, timeline, activity, start, end): 
        url = self.url('/client/%s/dash' % self.client)

        start = serializers.datetime(start)
        end = serializers.datetime(end)
        data = dict(
            timeline=timeline,
            activity=activity,
            start=start,
            end=end
        )

        response = requests.post(url, data=data)

        if 200 == response.status_code:
            data = response.content
            data = json.loads(data)
            return data

