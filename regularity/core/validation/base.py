
class InvalidTypeError(Exception):

    def __init__(self, value, type_, **kwargs):
        super(InvalidTypeError, self).__init__(**kwargs)
        self.value = value
        self.type = type_

class NullValueError(Exception): 
    pass

class ValidationError(Exception): 
    pass

class Field(object):
    '''Base class for the various fields.'''

    def __init__(self, type_, required=False, null=True):
        '''Create the field validator.

           @param type_ : type|tuple(type)
               the type of data this field represents
           @param required : optional, bool
               the flag controlling whether this field is required
               defaults to False
           @param null : optional, bool
               the flag controlling whether this field can be null
               defaults to True'''

        self.type = type_
        self.required = required
        self.null = null

    def _process(self, value):
        # check if the value is None and throw an error if this is not allowed
        if value is None:
            if not self.null:
                raise NullValueError

            return None

        else:
            if not isinstance(value, self.type):
                raise InvalidTypeError(value, self.type)

        return self.process(value)

    def process(self, value):
        return value

class DictField(Field):

    def __init__(self, subfields, **kwargs):
        '''Initialize the DictField.

           @param data : dict
               the dict to clean and validate'''
        
        super(DictField, self).__init__(dict, **kwargs)

        self.subfields = subfields

    def _validate_keys_(self, keys):
        '''Determine if the keys passed in are valid. They are invalid if they
           not a subset of the spec keys or they are missing a required key.

           @param keys : iterable(str)
               the keys to check'''

        keys = frozenset(keys)

        field_keys = set()
        required_keys = set()
        for key, field in self.subfields.iteritems():
            field_keys.add(key)

            if field.required:
                required_keys.add(key)

        # find any keys that aren't in the spec
        bad_keys = keys.difference(field_keys)
        if bad_keys:
            raise ValdationError('the following keys do not belong to the spec: %s' % ', '.join(bad_keys))

        # find any missing required keys
        missing_keys = required_keys.difference(keys)
        if missing_keys:
            raise ValidationError('the following required keys are missing: %s' % ', '.join(missing_keys))

    def process(self, value):
        self._validate_keys_(value.iterkeys())

        for key in value.iterkeys():
            field = self.subfields[key]
            value[key] = field._process(value[key])

        return value

class ListField(Field):

    def __init__(self, subfield, **kwargs):
        '''Initialize a ListField.'''

        super(ListField, self).__init__(list, **kwargs)

        self.subfield = subfield

    def process(self, value):
        if 0 == len(value) and self.subfield.required:
            raise ValidationError('list must contain at least one value')

        processed_values = list()
        for i in xrange(len(value)):
            v = self.subfield._process(value[i])
            processed_values.append(v)

        return processed_values

class IntField(Field):

    def __init__(self, **kwargs):
        '''Initialize an IntField.'''

        super(IntField, self).__init__((int, basestring), **kwargs)

    def process(self, value):
        try:
            return int(value)
        except ValueError:
            pass
        raise ValidationError('could not convert %s to int' % value)

class StringField(Field):

    def __init__(self, length=None, **kwargs):
        '''Initialize a StringField.

           @param length : optional, int
               the maximum length this field can be'''

        super(StringField, self).__init__(basestring, **kwargs)

        self.length = length

    def process(self, value):
        value = value.strip()
        if self.length is not None and len(value) > self.length:
            raise ValidationError('string is too long')

        return value

