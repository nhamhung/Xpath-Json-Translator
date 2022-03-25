from __future__ import unicode_literals, print_function, absolute_import, division, generators, nested_scopes
import unittest

from xpath.xpath_lexer import XpathLexer
from xpath.xpath_parser import XpathParser
from xpath.xpath_evaluator import *

class TestParser(unittest.TestCase):
    # TODO: This will be much more effective with a few regression tests and `arbitrary` parse . pretty testing

    @classmethod
    def setup_class(cls):
        logging.basicConfig()

    def check_parse_cases(self, test_cases):
        parser = XpathParser(debug=True, lexer_class=lambda:XpathLexer(debug=False)) # Note that just manually passing token streams avoids this dep, but that sucks

        for string, parsed in test_cases:
            print(string, '=?=', parsed) # pytest captures this and we see it only on a failure, for debugging
            assert parser.parse(string) == parsed

    def test_atomic(self):
        self.check_parse_cases([('foo', Field('foo')),
                                ('bar', Field('bar')),
                               ])

    def test_nested(self):
        self.check_parse_cases([('foo/baz', Child(Field('foo'), Field('baz'))),
                                ('foo//baz', Descendants(Field('foo'), Field('baz'))),
                                ('foo//baz/bing', Descendants(Field('foo'), Child(Field('baz'), Field('bing'))))])

if __name__ == '__main__':
    unittest.main()