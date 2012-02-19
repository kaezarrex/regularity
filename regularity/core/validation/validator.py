
from fields import DictField, Field

class ValidatorMeta(type):
    '''The metaclass for a validator. Takes a class definition and adds a
       validate method based off of the fields defined, while removing the 
       attributes that map to fields.'''

    def __new__(cls, name, parents, _attrs):

        attrs = dict()
        form_fields = dict()

        # iterate through the attributes in the class definition
        for key, value in _attrs.iteritems():

            if isinstance(value, Field):
                # set the name of the field, based on its name in the class
                # definition
                value.set_name(key)

                # add the field to the list of Fields
                form_fields[key] = value

            else:
                # it is not a field, include it in the new class definition
                attrs[key] = value

        # add the validate method to the new attribute list
        form = DictField(form_fields, required=True, null=False)
        attrs['validate'] = staticmethod(lambda d : form.process(d))

        return super(ValidatorMeta, cls).__new__(cls, name, parents, attrs)

class Validator(object):
    '''A object that all validators need to subclass'''

    __metaclass__ = ValidatorMeta
