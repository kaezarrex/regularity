import pymongo.objectid

from regularity.core.validation.fields import Field

class ObjectIdField(Field):
    '''A field for validating mongoDB object ids'''

    def __init__(self, **kwargs):
        '''Initialize an ObjectIdField.
        
           @param kwargs : keyword arguments
               arguments to pass on to the super class'''

        super(ObjectIdField, self).__init__((str, pymongo.objectid.ObjectId))

    def process(self, value):
        '''Attempt to convert the value into an ObjectId
           
           @param value : object
               the value to try to convert to an ObjectId'''

        try:
            return pymongo.objectid.ObjectId(value)
        except:
            pass

        raise ValidationError("could not convert '%s' to an object id" % value)

    



