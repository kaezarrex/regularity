import datetime
import unittest

from regularity.core.validation import \
    DateTimeField, DictField, ListField, IntField, StringField, Validator, \
    ValidationError
from regularity.core.validation.fields import Field

class TestField(unittest.TestCase):

    def test_process(self):

        f = Field(int, null=False)
        self.assertRaises(ValidationError, f._process, None)
        self.assertRaises(ValidationError, f._process, 5.4)
        self.assertEquals(5, f._process(5))

        f = Field(int, null=True)
        self.assertEquals(None, f._process(None))
        self.assertRaises(ValidationError, f._process, 5.4)
        self.assertEquals(5, f._process(5))

class TestDateTimeField(unittest.TestCase):

    def test_process(self):
        
        f = DateTimeField()

        now = datetime.datetime.utcnow()
        self.assertEquals(now, f.process(now))

class TestDictField(unittest.TestCase):

    def test_process(self):

        f = DictField({
            'name' : StringField(required=True),
            'age' : IntField(required=False)
        })

        v1 = dict(name='Tim')
        v2 = dict(name=25, age=25)
        v3 = dict(name='Tim', age='Tim')
        v4 = dict(name='Tim', age=25)
        v5 = dict(age=25)
        v6 = dict(name='Tim', age=25, extra='fail')

        self.assertEquals(dict(name='Tim'), f.process(v1))
        self.assertRaises(ValidationError, f.process, v2)
        self.assertRaises(ValidationError, f.process, v3)
        self.assertEquals(dict(name='Tim', age=25), f.process(v4))
        self.assertRaises(ValidationError, f.process, v5)
        self.assertRaises(ValidationError, f.process, v6)

class TestIntField(unittest.TestCase):

    def test_process(self):
        
        f = IntField()

        self.assertRaises(ValidationError, f.process, '')
        self.assertRaises(ValidationError, f.process, '  ')
        self.assertRaises(ValidationError, f.process, 'abc')
        self.assertRaises(ValidationError, f.process, ' abc ')

        self.assertEquals(5, f.process(5))
        self.assertEquals(5, f.process('5'))

class TestListField(unittest.TestCase):

    def test_process(self):

        f1 = ListField(StringField(required=True))
        f2 = ListField(StringField(required=False))

        self.assertRaises(ValidationError, f1.process, [])
        self.assertEquals([], f2.process([]))

        f3 = ListField(StringField(null=False))
        f4 = ListField(StringField(null=True))

        self.assertRaises(ValidationError, f3.process, [None])
        self.assertRaises(ValidationError, f3.process, ['a', 'b', None])

        self.assertEquals(['a', 'b', 'c'], f3.process(['a', 'b', 'c']))
        self.assertEquals(['a', 'b', 'c'], f4.process(['a', 'b', 'c']))
        self.assertEquals(['a', None, 'b', None, 'c'], f4.process(['a', None, 'b', None, 'c']))

class TestStringField(unittest.TestCase):

    def test_process(self):
        
        f = StringField(length=4)

        self.assertRaises(ValidationError, f.process, 'abcde')

        self.assertEquals('', f.process(''))
        self.assertEquals('', f.process('     '))
        self.assertEquals('abcd', f.process('abcd'))
        self.assertEquals('abcd', f.process('   abcd   '))

class TestValidator(unittest.TestCase):

    def test_initialization(self):
            
        name_field = StringField()
        age_field = IntField()

        int_field1 = IntField(required=False)
        int_field2 = IntField(required=False)
        list_field = ListField(int_field1, required=False)
        dict_field = DictField({'list' : list_field, 'i2' : int_field2}, required=False)

        class TestForm(Validator):
            name = name_field
            age = age_field
            d = dict_field
            
        self.assertNotIn('name', TestForm.__dict__)
        self.assertNotIn('age', TestForm.__dict__)
        self.assertIn('validate', TestForm.__dict__)

        form = TestForm()

        data = dict(
            name = '   Tim ',
            age = '25'
        )

        self.assertEqual('name', name_field.name)
        self.assertEqual('age', age_field.name)
        self.assertEqual('d', dict_field.name)
        self.assertEqual('d.i2', int_field2.name)
        self.assertEqual('d.list', list_field.name)
        self.assertEqual('d.list.element', int_field1.name)


        self.assertEqual({'name' : 'Tim', 'age' : 25}, TestForm.validate(data))
        self.assertEqual({'name' : 'Tim', 'age' : 25}, form.validate(data))

