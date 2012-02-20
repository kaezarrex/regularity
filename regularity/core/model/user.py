import hashlib
import random

import pymongo.objectid
from regularity.core.validation import StringField, Validator

from base import APIBase, validate
from fields import ObjectIdField

MIN_PASSWORD_LENGTH = 6
N_SALT_CHARS = 16

class UserAlreadyExists(Exception):
    '''An error for creating a user with an email that has already been 
       registered.'''

class UserValidator(Validator):
    '''The validator for user objects'''

    _id = ObjectIdField()
    email = StringField()

def combine_salt_password(salt, password):
    '''Combine the salt and password and then run through the hash function to
       generate a password hash.

       @param salt : unicode
           the salt to use in the hash
       @param password : unicode
           the password to use in the hash'''

    return unicode(hashlib.sha512(u'%s%s' % (salt, password)).hexdigest())

def generate_password_hash(password):
    '''Generate the hash of a password by salting it and then hashing it.
    
       @param password : unicode
           the password to hash'''

    salt = u'%x' % random.getrandbits(N_SALT_CHARS * 8)
    password_hash = combine_salt_password(salt, password)

    return salt, password_hash

class UserAPI(APIBase):

    @property
    def collection(self):
        '''Return the database collection for this API'''

        return self.db.users

    def object_by_id(self, object_id):
        '''Override the object_by_id function, as only one id is required when
           getting a user. Also exclude salt and password fields for security.

           @param object_id : str|pymongo.objectid.ObjectId
               the id of the user'''

        object_id = self.object_id(object_id)

        fields = {
            'salt' : 0,
            'password_hash' : 0
        }
        return self.collection.find_one({ '_id' : object_id}, fields)

    def create(self, email, password):
        '''Create a new user.
        
           @param email : str
               the email address of the user
           @param password : str
               the password of the user'''

        user = dict(
            _id=pymongo.objectid.ObjectId(),
            email=email,
        )

        user = UserValidator.validate(user)

        # make sure the email isn't already in the database
        query = self.collection.find({'email' : email})
        query = tuple(query)

        if query:
            raise UserAlreadyExists(email)

        salt, password_hash = generate_password_hash(password)
        user['salt'] = salt
        user['password_hash'] = password_hash

        self.collection.insert(user)

        return self.object_by_id(user['_id'])

    def authenticate(self, email, password):
        '''Authenticate a password to an email - hash the password and see if
           it matches what is stored in the database.

           @param email : str|unicode
               the email address of the user
           @param password : str|unicode
               the password to hash and match up'''
        
        email = unicode(email)
        password = unicode(password)

        fields = {
            '_id' : 1,
            'salt' : 1,
            'password_hash' : 1
        }
        data = self.collection.find_one({ 'email' : email }, fields)

        if data is None:
            return False

        password_hash = combine_salt_password(data['salt'], password)

        if password_hash == data['password_hash']:
            return self.object_by_id(data['_id'])

        return False

