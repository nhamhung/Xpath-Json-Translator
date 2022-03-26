from __future__ import unicode_literals, print_function, absolute_import, division, generators, nested_scopes
import logging
from sqlite3 import DatabaseError
from turtle import left, right
from numpy import isin
import six
from itertools import *  # noqa
from .exceptions import XpathPathError

# Get logger name
logger = logging.getLogger(__name__)

class Xpath(object):
    
    def find(self, data):
        raise NotImplementedError()
    
    def child(self, child):
        if isinstance(self, This) or isinstance(self, Root):
            return child
        elif isinstance(child, This):
            return self
        elif isinstance(child, Root):
            return child
        else:
            return Child(self, child)
    
class Root(Xpath):
    
    def __str__(self):
        return '/'

    def __repr__(self):
        return 'Root()'

    def __eq__(self, other):
        return isinstance(other, Root)

class Child(Xpath):
    """
    Concrete syntax <left> '/' <right>
    """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def find(self, datum):
        return self.right.find(self.left.find(datum))
        
    def __eq__(self, other):
        return isinstance(other, Child) and self.left == other.left and self.right == other.right

    def __str__(self):
        return '%s/%s' % (self.left, self.right)

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.left, self.right)

class Descendants(Xpath):

    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def find(self, data):
        left_match = self.left.find(data)
        
        def recursively_match(data, result):
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict):
                        result.extend(recursively_match(value, []))
                    elif key == self.right.field:
                        result.append(value)
            elif isinstance(data, list):
                for i in range(len(data)):
                    value = data[i]
                    result.extend(recursively_match(value, []))

            return result

        return [result for result in recursively_match(left_match, [])]

    def __str__(self):
        return '%s//%s' % (self.left, self.right)

    def __eq__(self, other):
        return isinstance(other, Descendants) and self.left == other.left and self.right == other.right

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.left, self.right)

class Field(Xpath):
    
    def __init__(self, field):
        self.field = field

    def find(self, data):
        return data.get(self.field)

    def __str__(self):
        return '%s' % (self.field)

    def __repr__(self):
        return '%s' % (self.field)

    def __eq__(self, other):
        return isinstance(other, Field) and self.field == other.field

class This(Xpath):

    def __str__(self):
        return '.'

    def __repr__(self):
        return 'This()'

    def __eq__(self, other):
        return isinstance(other, This)