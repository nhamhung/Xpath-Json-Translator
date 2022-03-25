from __future__ import (
    print_function,
    absolute_import,
    division,
    generators,
    nested_scopes,
)
import sys
import os.path

import ply.yacc
import logging
from xpath.exceptions import XpathParserError
from xpath.xpath_lexer import XpathLexer
from xpath.xpath_evaluator import *

logger = logging.getLogger(__name__)

def parse(string):
    return XpathParser().parse(string)

class XpathParser(object):
    tokens = XpathLexer.tokens

    def __init__(self, debug=False, lexer_class=None):
        self.debug = debug
        self.lexer_class = lexer_class or XpathLexer
    
    def parse(self, string, lexer=None):
        lexer = lexer or self.lexer_class()
        return self.parse_token_stream(lexer.tokenize(string))
    
    def parse_token_stream(self, token_iterator, start_symbol='xpath'):
        output_directory = os.path.dirname(__file__)
        try:
            module_name = os.path.splitext(os.path.split(__file__)[1])[0]
        except:
            module_name = __name__

        parsing_table_module = '_'.join([module_name, start_symbol, 'parsetab'])

        # And we regenerate the parse table every time; it doesn't actually take that long!
        new_parser = ply.yacc.yacc(module=self,
                                   debug=self.debug,
                                   tabmodule = parsing_table_module,
                                   outputdir = output_directory,
                                   write_tables=0,
                                   start = start_symbol,
                                   errorlog = logger)

        return new_parser.parse(lexer = IteratorToTokenStream(token_iterator))

    # lowest to highest precedence
    precedence = [
        ('left', 'DOUBLESLASH'),
        ('left', '/'),
    ]

    def p_error(self, t):
        raise XpathParserError('Parse error at %s:%s near token %s (%s)'
                            % (t.lineno, t.col, t.value, t.type))

    def p_xpath_binop(self, p):
        """xpath : xpath '/' xpath
                 | xpath DOUBLESLASH xpath"""
        
        op = p[2]
        
        if op == '/':
            p[0] = Child(p[1], p[3])
        elif op == '//':
            p[0] = Descendants(p[1], p[3])
    
    def p_jsonpath_root(self, p):
        "xpath : '/'"
        p[0] = Root()

    def p_xpath_field(self, p):
        "xpath : field"
        p[0] = Field(p[1])
    
    def p_field_id(self, p):
        "field : ID"
        p[0] = p[1]

class IteratorToTokenStream(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def token(self):
        try:
            return next(self.iterator)
        except StopIteration:
            return None

if __name__ == '__main__':
    logging.basicConfig()
    parser = XpathParser(debug=True)
    print(parser.parse('foo//baz/bar').__repr__())