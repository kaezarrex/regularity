from copy import deepcopy
import httplib
import json
import times
import urllib

import requests

import serializers as _serializers

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

def request(url, method, data=None, serializers=None):
    '''Simple function for making a POST request and handling different status
       codes.

       @param url : str
           the url to hit
       @param data : optional, dict
           the data to include
       @param serializers : dict
           a mapping of serializer functions for any fields that need so'''

    # serialize any fields that need so
    if data:
        data = _serializers.serialize(data, **serializers)

    method_fn = getattr(requests, method)
    response = method_fn(url, data=data)

    if 200 == response.status_code:
        data = response.content
        data = json.loads(data)

        if data:
            _serializers.serialize(data, **serializers)

        return data
    else:
        return None
    

class API(object):

    def __init__(self, host, port, timezone, client=None):
        '''Create the client-side api.

           @param host : str
               the url of the server
           @param port : int
               the port number
           @client : optional, str
               the client id to bind the API to'''

        self.base_url = 'http://%s:%d' % (host, port)
        self.timezone = timezone
        self.client = client

    def url(self, path, **kwargs):
        '''Form the url to hit for the API path.

           @param path : str
               the API path to hit'''

        url = '%s%s' % (self.base_url, path)

        if kwargs:
            query = dict((k,v) for k, v in kwargs.iteritems() if v)

            if query:
                query_string = urllib.urlencode(query)
                url = '%s?%s' % (url, query_string)

        return url

    def init(self):
        '''Register a new client on the server, and return the configuration
           information to store'''

        url = self.url('/client/create')

        data = request(url, 'post', serializers=dict(
            _id=_serializers.object_id
        ))

        return data
    
    @require_client
    def dots(self, name=None, limit=10):
        '''List the dots on the server for this client.
        
           @param name : optional, str
               the name of the activity to retrieve 
           @param limit : int
               the length to limit the results to'''

        url = self.url('/client/%s/dot' % self.client, name=name, limit=limit)

        data = request(url, 'get', serializers=dict(
            time=_serializers.datetime
        ))

        return self._localize_data(data, 'time')
    
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

        data = request(url, 'post', data=data, serializers=dict(
            time=_serializers.datetime
        ))

        return self._localize_datum(data, 'time')
    
    @require_client
    def dashes(self, name=None, limit=10):
        '''Get the dashes for this client.
        
           @param name : optional, str
               the name of the activity to retrieve 
           @param limit : int
               the length to limit the results to'''

        url = self.url('/client/%s/dash' % self.client, name=name, limit=limit)

        data = request(url, 'get', serializers=dict(
            start=_serializers.datetime,
            end=_serializers.datetime
        ))

        return self._localize_data(data, 'start', 'end')
    
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

        data = request(url, 'post', data=data, serializers=dict(
            start=_serializers.datetime,
            end=_serializers.datetime
        ))

        return self._localize_datum(data, 'start', 'end')

    @require_client
    def pendings(self, name=None, limit=10):
        '''List the pendings for this client.
        
           @param name : optional, str
               the name of the activity to retrieve 
           @param limit : int
               the length to limit the results to'''

        url = self.url('/client/%s/pending' % self.client, name=name, limit=limit)

        data = request(url, 'get', serializers=dict(
            start=_serializers.datetime
        ))

        return self._localize_data(data, 'start', 'end')
    
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

        url = self.url('/client/%s/pending' % self.client)

        data = dict(
            timeline=timeline,
            activity=activity,
            start=start,
        )

        data = request(url, 'post', data=data, serializers=dict(
            start=_serializers.datetime,
            end=_serializers.datetime,
        ))

        return self._localize_datum(data, 'start', 'end')

    def _localize_data(self, data, *args):
        '''Convert datetimes in data from UTC to another timezone

           @param data : iterable(dict)
               an iterable of dicts
           @param args : positional paramaters
               the keys to convert from UTC to another timezone'''

        _data = list()

        for d in data:
            _data.append(self._localize_datum(d, *args))

        return tuple(_data)

    def _localize_datum(self, datum, *args):
        '''Convert datetimes in one line of data from UTC to another timezone

           @param datum : dict
               a dict
           @param args : positional paramaters
               the keys to convert from UTC to another timezone'''

        _datum = deepcopy(datum)

        for arg in args:
            t = _datum.get(arg)
            if t is None:
                continue
            _datum[arg] = times.to_local(t, self.timezone)

        return _datum
