import datetime

import pymongo

class Model(object):
    '''The container class for the sub models'''

    def __init__(self, host='localhost', port=27017, user=None, password=None, database='regularity'):
        '''Create a connection to mongoDB

           @param host : optional, str
               the host of the mongoDB server, defaults to localhost
           @param port : optional, int
               the port of the mongoDB server, defaults to 27017
           @param user : optional, str
               the user to connect to mongoDB as, defaults to None
           @param password : optional, str
               the password for the user, defaults to None
           @param database : optional, str
               the name of the database to connect to, defaults to "regularity"'''

        connection = pymongo.Connection(host=host, port=port)
        db = pymongo.database.Database(connection, database)

        if user and password:
            success = db.authenticate(user, password)
            if not success:
                raise BaseException('could not authenticate')

        self.users = UserAPI(db)
        self.dots = DotAPI(db)
        self.dashes = DashAPI(db)
        self.pendings = PendingAPI(db)

    def finish_pending(self, pending, time=None):
        '''Finish a pending, and move it to the dashes collection.

           @param pending : dict
               the pending to finish
           @param time : optional, datetime.datetime
               the end time of the pending, defaults to now'''

        if time is None:
            time = datetime.datetime.utcnow()

        pending = self.pendings.verify(pending)
        self.pendings.remove(pending)

        dash = self.dashes.create(
            pending['user'], 
            pending['timeline'], 
            pending['name'], 
            pending['start'], 
            time=time, 
            note=pending.get('note')
        )
        
        return dash

    def search(self, user, search_dots=True, search_dashes=True, search_pendings=True, **kwargs):
        '''Search through the database for events that match the criteria.

           @param user : str|pymongo.objectid.ObjectId
               the name of the user whose events will be searched
           @param search_dots : optional, bool
               a flag controlling whether dots are searched
           @param search_dashes : optional, bool
               a flag controlling whether dashes are searched
           @param search_pendings : optional, bool
               a flag controlling whether pendings are searched
           @param kwargs : keyword arguments
               search criteria for the events to find:
               
               name : str
                   the name of the events to look for'''

        data = dict()

        if search_dots:
            dots = self.dots.search(user, **kwargs)
            data['dots'] = dots

        if search_dashes:
            dashes = self.dashes.search(user, **kwargs)
            data['dashes'] = dashes
        
        if search_pendings:
            pendings = self.pendings.search(user, **kwargs)
            data['pendings'] = pendings

        return data

