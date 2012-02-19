import datetime

class ValidationError(Exception): 
    '''The error that gets raised externally when data does not validate'''

    def __init__(self, *args):
        super(ValidationError, self).__init__(*args)

class Field(object):
    '''Base class for the various fields.'''

    def __init__(self, type_, required=True, null=False):
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

        # the name of the field will be set by the Validator class
        self.name = None

    def set_name(self, name):
        '''Set the name of the field, for debugging purposes.

           @param name : str
               the name for this field'''

        self.name = name

    def _raise_(self, message):
        '''Raise a validation error, inserting in the name if the field if it is
           defined.

           @param message : str
               the exception message'''

        if self.name:
            raise ValidationError('%s: %s' % (self.name, message))

        raise ValidationError(message)

    def _process(self, value):
        '''Perfom null validation and type validation, then hand the value off
           to the subclass' implementation of process for extra validation.

           @param value : object
               the object to process'''

        # check if the value is None and throw an error if this is not allowed
        if value is None:
            if not self.null:
                self._raise_('value cannot be null')

            return None

        else:
            if not isinstance(value, self.type):
                self._raise_('invalid type: %s (should be %s)' % (type(value), self.type))

        return self.process(value)

    def process(self, value):
        '''The identity function, meant to be subclassed for extra validation.'''

        return value

class DictField(Field):
    '''A field that validates a dictionary'''

    def __init__(self, subfields, **kwargs):
        '''Initialize the DictField.

           @param subfields : dict
               a mapping from str -> Field
           @param kwargs : keyword arguments
               arguments to pass on to the super class'''
        
        super(DictField, self).__init__(dict, **kwargs)

        self.subfields = subfields

    def set_name(self, name):
        '''Override the super method, also recursively setting the name of 
           subfields.

           @param name : str 
               the name for this field'''

        super(DictField, self).set_name(name)

        for key, value in self.subfields.iteritems():
            value.set_name('%s.%s' % (name, key))

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
            self._raise_('the following keys do not belong to the spec: %s' % ', '.join(bad_keys))

        # find any missing required keys
        missing_keys = required_keys.difference(keys)
        if missing_keys:
            self._raise_('the following required keys are missing: %s' % ', '.join(missing_keys))

    def process(self, value):
        '''Ensure the required keys are present, and that no extra keys are 
           present, then iterate through each key and validate it separately.

           @param value : dict
               the value to process'''

        self._validate_keys_(value.iterkeys())

        for key in value.iterkeys():
            field = self.subfields[key]
            value[key] = field._process(value[key])

        return value

class ListField(Field):
    '''A field that validates lists'''

    def __init__(self, subfield, **kwargs):
        '''Initialize a ListField.
        
           @param subfield : Field
               the field type for each element in the list
           @param kwargs : keyword arguments
               arguments to pass on to the super class'''

        super(ListField, self).__init__(list, **kwargs)

        self.subfield = subfield

    def set_name(self, name):
        '''Override the super method, also setting the name of the subfield.

           @param name : str 
               the name for this field'''

        super(ListField, self).set_name(name)
        self.subfield.set_name('%s.element' % name)

    def process(self, value):
        '''Iterate through each item in the list and verify that each one 
           validates.

           @param value : list
               the list to process'''

        if 0 == len(value) and self.subfield.required:
            self._raise_('list cannot be empty, because the subfield was defined as required')

        processed_values = list()
        for i in xrange(len(value)):
            v = self.subfield._process(value[i])
            processed_values.append(v)

        return processed_values

class IntField(Field):
    '''A field that validates integers'''

    def __init__(self, **kwargs):
        '''Initialize an IntField.

           @param kwargs : keyword arguments
               arguments to pass on to the super class'''

        super(IntField, self).__init__((int, basestring), **kwargs)

    def process(self, value):
        '''Attempt to convert the value to an int.

           @param value : str|int
               the value to attempt to convert'''

        try:
            return int(value)
        except ValueError:
            pass
        self._raise_('could not convert %s to int' % value)

class StringField(Field):
    '''A field that validates strings'''

    def __init__(self, length=None, **kwargs):
        '''Initialize a StringField.

           @param length : optional, int
               the maximum length this field can be
           @param kwargs : keyword arguments
               arguments to pass on to the super class'''

        super(StringField, self).__init__(basestring, **kwargs)

        self.length = length

    def process(self, value):
        '''Valdate the length of the string does not exceed the maximum, if it
           is set.

           @param value : str
               the string to validate'''

        value = value.strip()
        if self.length is not None and len(value) > self.length:
            self._raise_('string is longer than %d characters: %s' % (self.length, value))

        return value

class DateTimeField(Field):
    '''A field that validates datetimes'''

    def __init__(self, **kwargs):
        '''Initialize a DateTimeField.
           
           @param kwargs : keyword arguments
               arguments to pass on to the super class'''

        super(DateTimeField, self).__init__(datetime.datetime, **kwargs)


