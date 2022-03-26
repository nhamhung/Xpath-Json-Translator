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
                assert [r for r in result] == target
            else:
                assert result == target

    def test_fields_value(self):
        self.check_cases([ 
            ('foo', {'foo': 'baz'}, 'baz'),
         ])
    
    def test_child_value(self):
        self.check_cases([('foo/baz', {'foo': {'baz': 3}}, 3),
                          ('foo/baz', {'foo': {'baz': [3]}}, [3]),
                          ('foo/baz/bizzle', {'foo': {'baz': {'bizzle': 5}}}, 5)])
    
    def test_descendants_value(self):
        self.check_cases([ 
            ('foo//baz', {'foo': {'baz': 1, 'bing': {'baz': 2}}}, [1, 2] ),
            ('foo//baz', {'foo': [{'baz': 1}, {'baz': 2}, {'baz': 3, 'boo': 5}]}, [1, 2, 3] ), 
        ])

if __name__ == '__main__':
    unittest.main()