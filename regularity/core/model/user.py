import pymongo.objectid
from regularity.core.validation import StringField, Validator

from base import APIBase, validate
from fields import ObjectIdField

class User(Validator):
    '''The validator for user objects'''

    _id = ObjectIdField()
    email = StringField()
    password = StringField()

class UserAPI(APIBase):

    @property
    def collection(self):
        '''Return the database collection for this API'''

        return self.db.users

    def create(self, email, password):
        '''Create a new user.
        
           @param email : str
               the email address of the user
           @param password : str
               the password of the user'''

        user = dict(
            _id=pymongo.objectid.ObjectId(),
            email=email,
            password=password
        )
        user = User.validate(user)

        self.collection.insert(user)
        return user

