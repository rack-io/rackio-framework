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
STRING = "str"


class Tag:
    def __init__(self, name, value, _type, units, desc=""):
        self.name = name
        self.value = value
        self.units = units
        self._type = _type

        self.description = desc

        self._observers = set()

    def set_value(self, value):
        self.value = value
        self.notify()

    def get_value(self):
        return self.value

    def get_type(self):
        return self._type

    def get_units(self):
        return self.units

    def get_description(self):
        return self.description

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


class PropertyType:

    """
    Implement an abstract propery type
    """

    def __init__(self, _type, default=None):
        self._type = _type
        self.default = default


class StringType(PropertyType):

    """
    Implement a Float Type
    """

    def __init__(self, default=None):
        super(StringType, self).__init__(STRING, default)


class FloatType(PropertyType):

    """
    Implement a Float Type
    """

    def __init__(self, default=None):
        super(FloatType, self).__init__(FLOAT, default)


class IntegerType(PropertyType):

    """
    Implement an Integer Typle
    """

    def __init__(self, default=None):
        super(IntegerType, self).__init__(INTEGER, default)


class BooleanType(PropertyType):

    """
    Implement a Boolean Type
    """

    def __init__(self, default=None):
        super(BooleanType, self).__init__(BOOL, default)


class Model(object):

    """
    Implement an abstract model for inheritance
    """

    def __init__(self, **kwargs):
        attrs = self.get_attributes()

        for key, value in attrs.items():
            if key in kwargs:
                default = kwargs[key]
            else:
                try:
                    default = value.default
                    _type = value._type
                except Exception as e:
                    continue

            if default:
                setattr(self, key, default)
            else:
                if _type == FLOAT:
                    setattr(self, key, 0.0)
                elif _type == INTEGER:
                    setattr(self, key, 0)
                elif _type == BOOL:
                    setattr(self, key, False)
                elif _type == STRING:
                    setattr(self, key, "")

        self.attrs = attrs

    def __getattribute__(self, attr):
        method = object.__getattribute__(self, attr)

        if not method:
            return method

        if callable(method):

            def new_method(*args, **kwargs):
                result = method(*args, **kwargs)
                name = method.__name__

                if ("__" not in name) and (name != "save"):
                    try:
                        self.save()
                    except Exception as e:
                        pass

                return result

            return new_method
        else:
            return method

    def __copy__(self):
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        return newone

    @classmethod
    def get_attributes(cls):
        result = dict()

        props = cls.__dict__

        for key, value in props.items():
            if hasattr(value, "__call__"):
                continue
            if isinstance(value, cls):
                continue
            if not ismethod(value):
                if "__" not in key:
                    result[key] = value

        return result

    def commit(self):
        from .engine import CVTEngine

        _cvt = CVTEngine()

        try:
            _cvt.write_tag(self.tag, self)
            return True
        except Exception as e:
            return False

    def set_attr(self, name, value):
        setattr(self, name, value)

    def get_attr(self, name):
        result = getattr(self, name)
        return result

    @classmethod
    def set(cls, tag, obj):
        obj.tag = tag

    @classmethod
    def get(cls, tag):
        from .engine import CVTEngine

        _cvt = CVTEngine()

        return _cvt.read_tag(tag)

    def save(self):
        from .engine import CVTEngine

        _cvt = CVTEngine()

        try:
            tag = self.tag

            _cvt.write_tag(tag, self)
        except Exception as e:
            raise KeyError

    def serialize(self):
        result = dict()

        attrs = self.get_attributes()

        for key in attrs:
            value = getattr(self, key)
            result[key] = value

        return result

    def _load(self, values):
        for key, value in values.items():
            setattr(self, key, value)
