import httplib
import json
import urllib

class API(object):

    def __init__(self, host, port):
        self.connection = httplib.HTTPConnection(host, port)

    def close(self):
        self.connection.close()

    def init(self):
        headers = {
            'Content-Type' : 'application/x-www-form-encoded/json',
            'Accept' : 'application/json'
        }

        self.connection.request('POST', '/client/create', None, headers)
        response = self.connection.getresponse()

        data = response.read()
        data = json.loads(data)

        return data

