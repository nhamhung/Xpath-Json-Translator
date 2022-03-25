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
    
    def find_or_create(self, data):
        return self.find(data)
    
    def make_datum(self, value):
        if isinstance(value, DatumInContext):
            return value
        else:
            return DatumInContext(value, path=Root(), context=None)
    
    def child(self, child):
        if isinstance(self, This) or isinstance(self, Root):
            return child
        elif isinstance(child, This):
            return self
        elif isinstance(child, Root):
            return child
        else:
            return Child(self, child)
    
class DatumInContext(object):
    
    @classmethod
    def wrap(cls, data):
        """
        Create a DatumInContext object on data
        """
        if isinstance(data, cls):
            return data
        else:
            return cls(data)
    
    def __init__(self, value, path=None, context=None):
        self.value = value
        self.path = path or This()
        self.context = None if context is None else DatumInContext.wrap(context)
    
    def in_context(self, context, path):
        """
        Context is parent of current Datum. If current Datum already has a context, wrap current context as grandparent
        To place `datum` within another, use `datum.in_context(context=..., path=...)`
        which extends the path. If the datum already has a context, it places the entire
        context within that passed in, so an object can be built from the inside out.
        """
        context = DatumInContext.wrap(context)

        if self.context:
            return DatumInContext(value=self.value, path=self.path, context=context.in_context(path=path, context=context))
        else: # if current datum has no parent context, wrap current datum in this context
            return DatumInContext(value=self.value, path=path, context=context)
    
    @property
    def full_path(self):
        return self.path if self.context is None else self.context.full_path.child(self.path)

    def __repr__(self):
        return '%s(value=%r, path=%r, context=%r)' % (self.__class__.__name__, self.value, self.path, self.context)

    def __eq__(self, other):
        return isinstance(other, DatumInContext) and other.value == self.value and other.path == self.path and self.context == other.context
    
class Root(Xpath):
    
    def __str__(self):
        return '/'

    def find(self, datum):
        if not isinstance(datum, DatumInContext):
            return DatumInContext(datum, path=Root(), context=None)
        else:
            if datum.context is None:
                return DatumInContext(datum.value, context=None, path=Root())
            else:
                return Root().find(datum.context)

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
    
    def find(self, datum):
        left_match = self.left.find(datum)
        
        def recursively_match(datum, result):
            if isinstance(datum.value, dict):
                for key, value in datum.value.items():
                    if isinstance(value, dict):
                        result.extend(recursively_match(DatumInContext(value, context=datum, path=Field(key)), []))
                    else:
                        result.append(self.right.find(datum))
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

    def find(self, datum):
        datum = DatumInContext.wrap(datum)
        field_value = datum.value.get(self.field)
        return DatumInContext(field_value, path=Field(self.field), context=datum)

    def __str__(self):
        return '%s' % (self.field)

    def __repr__(self):
        return '%s' % (self.field)

    def __eq__(self, other):
        return isinstance(other, Field) and self.field == other.field

class This(Xpath):

    def find(self, datum):
        return [DatumInContext.wrap(datum)]

    def update(self, data, val):
        return val

    def filter(self, fn, data):
        return data if fn(data) else None

    def __str__(self):
        return '.'

    def __repr__(self):
        return 'This()'

    def __eq__(self, other):
        return isinstance(other, This)