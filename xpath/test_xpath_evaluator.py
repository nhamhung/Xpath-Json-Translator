from __future__ import unicode_literals, print_function, absolute_import, division, generators, nested_scopes
import unittest

from xpath.xpath_parser import parse
from xpath.xpath_evaluator import *
from xpath.xpath_lexer import XpathLexer

class TestDatumInContext(unittest.TestCase):
    """
    Tests of properties of the DatumInContext and AutoIdForDatum objects
    """
    
    @classmethod
    def setup_class(cls):
        logging.basicConfig()

    def test_DatumInContext_init(self):

        test_datum1 = DatumInContext(3)
        assert test_datum1.value == 3
        assert test_datum1.path == This()
        assert test_datum1.full_path == This()
        
        test_datum2 = DatumInContext(3, path=Root())
        assert test_datum2.value == 3
        assert test_datum2.path == Root()
        assert test_datum2.full_path == Root()

        test_datum3 = DatumInContext(3, path=Field('foo'), context='does not matter')
        assert test_datum3.value == 3
        assert test_datum3.path == Field('foo')
        assert test_datum3.full_path == Field('foo')

        test_datum3 = DatumInContext(3, path=Field('foo'), context=DatumInContext('does not matter', path=Field('baz'), context='does not matter'))
        assert test_datum3.path == Field('foo')
        assert test_datum3.full_path == Field('baz').child(Field('foo'))

    def test_DatumInContext_in_context(self):

        assert (DatumInContext(3).in_context(path=Field('foo'), context=DatumInContext('whatever'))
                ==
                DatumInContext(3, path=Field('foo'), context=DatumInContext('whatever')))

        assert (DatumInContext(3).in_context(path=Field('foo'), context='whatever').in_context(path=Field('baz'), context='whatever')
                ==
                DatumInContext(3).in_context(path=Field('foo'), context=DatumInContext('whatever').in_context(path=Field('baz'), context='whatever')))

class TestXpath(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logging.basicConfig()

    #
    # Check that the data value returned is good
    #
    def check_cases(self, test_cases):
        for string, data, target in test_cases:
            print('parse("%s").find(%s) =?= %s' % (string, data, target))
            result = parse(string).find(data)
            if isinstance(result, list):
                assert [r.value for r in result] == target
            else:
                assert result.value == target

    def test_fields_value(self):
        self.check_cases([ 
            ('foo', {'foo': 'baz'}, 'baz'),
         ])
    
    def test_root_value(self):
        self.check_cases([ 
            ('/', {'foo': 'baz'}, {'foo':'baz'}),
        ])
    
    def test_child_value(self):
        self.check_cases([('foo/baz', {'foo': {'baz': 3}}, 3),
                          ('foo/baz', {'foo': {'baz': [3]}}, [3]),
                          ('foo/baz/bizzle', {'foo': {'baz': {'bizzle': 5}}}, 5)])
    
    def test_descendants_value(self):
        self.check_cases([ 
            ('foo//baz', {'foo': {'baz': 1, 'bing': {'baz': 2}}}, [1, 2] ),
            # ('foo//baz', {'foo': [{'baz': 1}, {'baz': 2}]}, [1, 2] ), 
        ])

if __name__ == '__main__':
    unittest.main()