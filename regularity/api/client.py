import httplib
import json
import urllib

import requests

from regularity import serializers

def require_client(func):
    '''Wrap a function to check that requires the API to be bound to a client.
       Does the necessary checking and throws an error if it is not bound to a
       client.

       @param func: function
           the function to decorate'''

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
        '''Create the client-side api.

           @param host : str
               the url of the server
           @param port : int
               the port number
           @client : optional, str
               the client id to bind the API to'''

        self.base_url = 'http://%s:%d' % (host, port)
        self.client = client

    def url(self, path):
        '''Form the url to hit for the API path.

           @param path : str
               the API path to hit'''

        return '%s%s' % (self.base_url, path)

    def init(self):
        '''Register a new client on the server, and return the configuration
           information to store'''

        url = self.url('/client/create')

        data = post(url)

        return data
    
    @require_client
    def dot(self, timeline, activity, time): 
        '''Send a dot (an instantaneous event) to the server. 
           
           @param timeline : str
               the timeline the event belongs to
           @param activity : str
               the name of the activity
           @param time : datetime
               the UTC time of the event'''

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
        '''Send a ranged event (one that has a duration) to the server.

           @param timeline : str
               the timeline the event belongs to
           @param activity : str
               the name of the activity
           @param start : datetime
               the UTC time of the start of the activity
           @param end : datetime
               the UTC time of the end of the activity'''

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
    
    @require_client
    def pending(self, timeline, activity, start): 
        '''Send a pending event (one whose end time is not known yet) to the 
           server

           @param timeline : str
               the timeline the event belongs to
           @param activity : str
               the name of the activity
           @param start : datetime
               the UTC time of the start of the activity'''

        url = self.url('/client/%s/defer' % self.client)

        data = dict(
            timeline=timeline,
            activity=activity,
            start=start,
        )

        data = post(url, data=data, serializers=dict(
            start=serializers.datetime,
        ))

        return data

