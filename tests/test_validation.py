import unittest

from regularity.core.validation import DictField, ListField, IntField, StringField, InvalidTypeError, NullValueError, ValidationError
from regularity.core.validation.base import Field

class TestField(unittest.TestCase):

    def test_process(self):

        f = Field(int, null=False)
        self.assertRaises(NullValueError, f._process, None)
        self.assertRaises(InvalidTypeError, f._process, 5.4)
        self.assertEquals(5, f._process(5))

        f = Field(int, null=True)
        self.assertEquals(None, f._process(None))
        self.assertRaises(InvalidTypeError, f._process, 5.4)
        self.assertEquals(5, f._process(5))

class TestIntField(unittest.TestCase):

    def test_clean(self):
        
        f = IntField()

        self.assertRaises(ValidationError, f.process, '')
        self.assertRaises(ValidationError, f.process, '  ')
        self.assertRaises(ValidationError, f.process, 'abc')
        self.assertRaises(ValidationError, f.process, ' abc ')

        self.assertEquals(5, f.process(5))
        self.assertEquals(5, f.process('5'))

class TestStringField(unittest.TestCase):

    def test_process(self):
        
        f = StringField(length=4)

        self.assertRaises(ValidationError, f.process, 'abcde')

        self.assertEquals('', f.process(''))
        self.assertEquals('', f.process('     '))
        self.assertEquals('abcd', f.process('abcd'))
        self.assertEquals('abcd', f.process('   abcd   '))

class TestListField(unittest.TestCase):

    def test_process(self):

        f1 = ListField(StringField(required=True))
        f2 = ListField(StringField(required=False))

        self.assertRaises(ValidationError, f1.process, [])
        self.assertEquals([], f2.process([]))

        f3 = ListField(StringField(null=False))
        f4 = ListField(StringField(null=True))

        self.assertRaises(NullValueError, f3.process, [None])
        self.assertRaises(NullValueError, f3.process, ['a', 'b', None])

        self.assertEquals(['a', 'b', 'c'], f3.process(['a', 'b', 'c']))
        self.assertEquals(['a', 'b', 'c'], f4.process(['a', 'b', 'c']))
        self.assertEquals(['a', None, 'b', None, 'c'], f4.process(['a', None, 'b', None, 'c']))

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

        self.assertEquals(dict(name='Tim'), f.process(v1))
        self.assertRaises(InvalidTypeError, f.process, v2)
        self.assertRaises(ValidationError, f.process, v3)
        self.assertEquals(dict(name='Tim', age=25), f.process(v4))
