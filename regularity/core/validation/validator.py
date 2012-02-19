
from fields import DictField, Field

class ValidatorMeta(type):
    '''The metaclass for a validator. Takes a class definition and adds a
       validate method based off of the fields defined, while removing the 
       attributes that map to fields.'''

    def __new__(cls, name, parents, _attrs):

        attrs = dict()
        form_fields = dict()

        for key, value in _attrs.iteritems():
            if isinstance(value, Field):
                form_fields[key] = value
            else:
                attrs[key] = value

        form = DictField(form_fields, required=True, null=False)
        @staticmethod
        def validate(data):
            return form.process(data)

        attrs['validate'] = validate

        return super(ValidatorMeta, cls).__new__(cls, name, parents, attrs)

class Validator(object):
    '''A object that all validators need to subclass'''

    __metaclass__ = ValidatorMeta
