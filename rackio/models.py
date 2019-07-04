# -*- coding: utf-8 -*-
"""rackio/models.py

This module implements a Tags and other classes for
modelling the subjects involved in the core of the engine.
"""
from inspect import ismethod

from .utils import Observer

FLOAT = "float"
INTEGER = "int"
BOOL = "bool"

class Tag:

    def __init__(self, name, value, _type):

        self.name = name
        self.value = value
        self._type = _type

        self._observers = set()

    def set_value(self, value):

        self.value = value
        self.notify()
    
    def get_value(self):
        
        return self.value

    def get_type(self):
        
        return self._type
    
    def attach(self, observer):

        observer._subject = self
        self._observers.add(observer)

    def detach(self, observer):

        observer._subject = None
        self._observers.discard(observer)

    def notify(self):

        for observer in self._observers:

            observer.update()


class TagObserver(Observer):
    """
    Implement the Observer updating interface to keep its state
    consistent with the subject's.
    Store state that should stay consistent with the subject's.
    """
    def __init__(self, tag_queue):

        super(TagObserver, self).__init__()
        self._tag_queue = tag_queue

    def update(self):

        """
        This methods inserts the changing Tag into a 
        Producer-Consumer Queue Design Pattern
        """
        
        result = dict()

        result["tag"] = self._subject.name
        result["value"] = self._subject.value

        self._tag_queue.put(result)

# Classes for Custom models design


class PropertyField:

    """
    Implement an abstract propery field
    """

    def __init__(self, _type, default=None):

        self._type = _type
        self.default = default


class FloatField(PropertyField):

    """
    Implement a Float Field
    """

    def __init__(self, default=None):

        super(FloatField, self).__init__(FLOAT, default)


class IntegerField(PropertyField):

    """
    Implement an Integer Field
    """

    def __init__(self, default=None):

        super(IntegerField, self).__init__(INTEGER, default)

        
class BooleanField(PropertyField):

    """
    Implement a Boolean Field
    """

    def __init__(self, default=None):

        super(BooleanField, self).__init__(BOOL, default)


class Model:

    """
    Implement an abstract model for inheritance
    """

    def __new__(cls, *args, **kwargs):

        from .engine import CVTEngine

        _cvt = CVTEngine()
        _cvt.set_type(cls.__name__)

    def __init__(self, **kwargs):

        attrs = self.get_attributes()

        for key, value in attrs.items():

            if key in kwargs:
                default = kwargs[key]
            else:
                default = value.default
                _type = value._type

            if default:
                setattr(self, key, default)
            else:
                if _type == FLOAT:
                    setattr(self, key, 0.0)
                elif _type == INTEGER:
                    setattr(self, key, 0)
                elif _type == BOOL:
                    setattr(self, key, False)

        self.attrs = attrs

    @classmethod
    def get_attributes(cls):

        result = dict()
        
        props = cls.__dict__

        for key, value in props.items():

            if not ismethod(value):

                if not "__" in key:
                    result[key] = value

        return result
    
    def commit(self):

        pass

    @classmethod
    def set(cls, tag, obj):

        obj.tag = tag

    @classmethod
    def get(cls, tag):

        pass

    def save(self):

        pass

    def _serialize(self):

        result = dict()

        attrs = self.get_attributes()

        for key in attrs.keys():
            result[key] = getattr(self, key)

        return result
