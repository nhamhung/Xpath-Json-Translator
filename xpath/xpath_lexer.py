from __future__ import unicode_literals, print_function, absolute_import, division, generators, nested_scopes
import sys
import logging

import ply.lex

logger = logging.getLogger(__name__)

class XpathLexer(object):
    '''
    A Lexical analyzer for Xpath.
    '''

    def __init__(self, debug=False):
        self.debug = debug
    
    def tokenize(self, string):
        new_lexer = ply.lex.lex(module=self, debug=self.debug, errorlog=logger)
        new_lexer.latest_newline = 0
        new_lexer.string_value = None
        new_lexer.input(string)

        while True:
            t = new_lexer.token()
            if t is None: 
                break
            t.col = t.lexpos - new_lexer.latest_newline
            yield t
        
        if new_lexer.string_value is not None:
            raise Exception('Unexpected EOF in string literal or identifier')

    literals = ['/', '[', ']', '>', '<', '(', ')']

    reserved_words = {'and': 'AND', 'or': 'OR', 'count': 'COUNT'}

    tokens = ['ID', 'DOUBLESLASH', 'DOUBLECOLON', 'NUMBER', 'MOREEQUAL', 'LESSEQUAL'] + list(reserved_words.values())

    t_DOUBLESLASH = r'\/\/'
    t_DOUBLECOLON = r'\:\:'
    t_MOREEQUAL = r'\>\='
    t_LESSEQUAL = r'\<\='
    t_ignore = ' \t'

    def t_ID(self, t):
        r'[a-zA-Z_@][a-zA-Z0-9_@\-]*'
        t.type = self.reserved_words.get(t.value, 'ID')
        return t
    
    def t_NUMBER(self, t):
        r'-?\d+'
        t.value = int(t.value)
        return t
    
    def t_error(self, t):
        raise Exception('Error on line %s, col %s: Unexpected character: %s ' % (t.lexer.lineno, t.lexpos - t.lexer.latest_newline, t.value[0]))
    
if __name__ == '__main__':
    lexer = XpathLexer()
    print(lexer.__doc__)
    for token in lexer.tokenize('foo//bar::test'):
        print('%-20s%s' % (token.value, token.type))