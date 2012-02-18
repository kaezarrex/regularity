

class ValidationError(Exception): pass

class Validator(object):
    '''Base class for cleaning and validating dicts.'''

    def __init__(self, data):
        '''Create the validator.

           @param data : dict
               the dict to clean and validate'''
        
        if not isinstance(data, dict):
            raise ValidationError('data is not a dict')

        self.validate_keys(data.iterkeys())

        self.check_types(data)
        self.clean(data)
        self.validate(data)

    def validate_keys(self, keys):
        '''Determine if the keys passed in are valid. They are invalid if they
           not a subset of the spec keys or they are missing a required key.

           @param keys : iterable(str)
               the keys to check'''

        keys = frozenset(keys)

        spec_keys = set()
        required_keys = set()
        for key, field in self.spec.iteritems():
            spec_keys.add(key)

            if field.required:
                required_keys.add(key)

        # find any keys that aren't in the spec
        bad_keys = keys.difference(spec_keys)
        if bad_keys:
            raise ValdationError('the following keys do not belong to the spec: %s' % ', '.join(bad_keys))

        # find any missing required keys
        missing_keys = required_keys.difference(keys)
        if missing_keys:
            raise ValidationError('the following required keys are missing: %s' % ', '.join(missing_keys))

    def check_types(self, data):
        for key, value in data.iteritems():
            field = self.spec[key]
            field._check_type(value)

    def clean(self, data):
        for key, value in data.iteritems():
            field = self.spec[key]
            cleaned_value = field._clean(value)
            data[key] = cleaned_value

    def validate(self, data):
        for key, value in data.iteritems():
            field = self.spec[key]
            field._validate(value)

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

    def _check_type(self, value):
        if value is not None:
            if not isinstance(value, self.type):
                raise ValidationError('wrong type - %s should be %s' % (type(value), self.type))
            self.check_type(value)

    def check_type(self, value):
        pass

    def _clean(self, value):
        if value is None:
            return None
        return self.clean(value)

    def clean(self, value):
        return value

    def _validate(self, value):
        if value is None and not self.null:
            raise ValidationError('value cannot be None')

        self.validate(value)

    def validate(self, value):
        pass

class ListField(Field):

    def __init__(self, subfield, **kwargs):
        '''Initialize a ListField.'''

        super(ListField, self).__init__(list, **kwargs)

        self.subfield = subfield

    def check_type(self, value):
        for v in value:
            self.subfield._check_type(v)

    def clean(self, value):
        cleaned_values = list()
        for v in value:
            cleaned_values.append(self.subfield._clean(v))

        return cleaned_values

    def validate(self, value):
        for v in value:
            self.subfield._validate(v)

class DictField(Field):

    def __init__(self, subfields, **kwargs):
        '''Intialize a DictField.'''

        super(DictField, self).__init__(dict, **kwargs)

        self.subfields = dict(subfields)

    def check_type(self, value):
        for key, v in value.iteritems():
            subfield = self.subfields[key]
            subfield._check_type(v)

    def clean(self, value):
        cleaned_values = dict()
        for key, v in value.iteritems():
            subfield = self.subfields[key]
            cleaned_values[key] = subfield._clean(v)

        return cleaned_values

    def validate(self, value):
        for key, v in value.iteritems():
            subfield = self.subfields[key]
            subfield._validate(value)

class StringField(Field):

    def __init__(self, length=None, **kwargs):
        '''Initialize a StringField.

           @param length : optional, int
               the maximum length this field can be'''

        super(StringField, self).__init__(basestring, **kwargs)

        self.length = length

    def clean(self, value):
        value = value.strip()

        if not value:
            return None

        return value

    def validate(self, value):
        if self.length is not None:
            if len(value) > self.length:
                raise ValidationError('string is too long')

class IntField(Field):

    def __init__(self, **kwargs):
        '''Initialize an IntField.'''

        super(IntField, self).__init__((int, basestring), **kwargs)

    def clean(self, value):
        try:
            return int(value)
        except ValueError:
            pass
        raise ValidationError('could not convert %s to int' % value)

