# -*- coding: utf-8 -*-
"""rackio/engine.py

This module implements a Current Value Table (CVT), for holding current
tag values, in a thread safe implementation for Data Acquisition,
Database logging, Math operations and others real time processes.
"""
import threading
import logging
import copy

from ._singleton import Singleton
from .models import Tag


class CVT:
    """Current Value Table class for Tag based repository.

    This class is intended hold in memory tag based values and 
    observers for those required tags, this class is intended to be
    used by Rackio itself and not for other purposes

    # Example
    
    ```python
    >>> from rackio.engine import CVT
    >>> _cvt = CVT()
    ```

    """

    def __init__(self):

        self._tags = dict()
        self._types = ["float", "int", "bool", "str"]

    def set_type(self, _type):

        self._types.append(_type)
        self._types = list(set(self._types))

    def tag_defined(self, name):

        return name in self._tags.keys()

    def set_tag(self, name, _type, units=""):
        """Initialize a new Tag object in the _tags dictionary.
        
        # Parameters
        name (str):
            Tag name.
        _type (str): 
            Tag value type ("int", "float", "bool", "str")
        """

        if isinstance(_type, str):
        
            if _type in self._types:
                if _type == "float":
                    value = 0.0
                elif _type == "int":
                    value = 0
                elif _type == "str":
                    value = ""
                else:
                    value = False

        else:
            value = _type()
            _type.set(name, value)
            _type = _type.__name__
            self.set_type(_type)

        tag = Tag(name, value, _type, units)

        self._tags[name] = tag

    def set_tags(self, tags):
        """Initialize a list of new Tags object in the _tags dictionary.
        
        # Parameters
        tags (list):
            List of (tag, _type).
        """

        for name, _type in tags:
            self.set_tag(name, _type)

    def get_tags(self):
        """Returns a list of the defined tags names.
        """

        return self._tags.keys()

    def set_value(self, name, value):
        """Sets a new value for a defined tag.
        
        # Parameters
        name (str):
            Tag name.
        value (float, int, bool): 
            Tag value ("int", "float", "bool")
        """

        if "." in name:
            values = name.split(".")
            tag_name = values[0]
        else:
            tag_name = name
        
        if tag_name not in self._tags:
            raise KeyError

        if "." in name:
            values = name.split(".")
            name = values[0]
            _property = values[1]
            setattr(self._tags[name].value, _property, value)
            self._tags[name].notify()

        else:
            _type = self._tags[name].get_type()

            if _type not in self._types:
                value = copy.copy(value)
                value.tag = name
                
            self._tags[name].set_value(value)

    def get_value(self, name):
        """Returns a tag value defined by name.
        
        # Parameters
        name (str):
            Tag name.
        """
        
        if "." in name:
            values = name.split(".")
            name = values[0]
            _property = values[1]
            _new_object = copy.copy(getattr(self._tags[name].value, _property))
        else:
            _new_object = copy.copy(self._tags[name].get_value())
        
        return _new_object

    def get_type(self, name):
        """Returns a tag type defined by name.
        
        # Parameters
        name (str):
            Tag name.
        """

        return self._tags[name].get_type()

    def get_units(self, name):

        """Returns the units defined by name.
        
        # Parameters
        name (str):
            Tag name.
        """

        return self._tags[name].get_units()

    def get_types(self):
        """Returns all tag types.
        
        # Parameters
        """

        return self._types

    def attach_observer(self, name, observer):
        """Attaches a new observer to a tag object defined by name.
        
        # Parameters
        name (str):
            Tag name.
        observer (TagObserver): 
            Tag observer object, will update once a tag object is changed.
        """

        self._tags[name].attach(observer)

    def detach_observer(self, name, observer):
        """Detaches an observer from a tag object defined by name.
        
        # Parameters
        name (str):
            Tag name.
        observer (TagObserver): 
            Tag observer object.
        """
        self._tags[name].attach(observer)


class CVTEngine(Singleton):
    """Current Value Table Engine class for Tag thread-safe based repository.

    This class is intended hold in memory tag based values and 
    observers for those required tags, it is implemented as a singleton
    so each sub-thread within the Rackio application can access tags
    in a thread-safe mechanism.

    # Example
    
    ```python
    >>> from rackio.engine import CVTEngine
    >>> tag_egine = CVTEngine()
    >>> tag_engine.write_tag("TAG1", 40.43)
    >>> value = tag_engine.read_tag("TAG1")
    >>> print(value)
    40.43
    ```

    """

    def __init__(self):

        super(CVTEngine, self).__init__()

        self._cvt = CVT()
        self._groups = dict()
        self._request_lock = threading.Lock()
        self._response_lock = threading.Lock()

        self._response = None

        self._response_lock.acquire()

    def set_type(self, _type):
        """Sets a new type as string format.
        
        # Parameters
        _type (str):
            Type.
        """
        if _type not in self._cvt.get_types():
            self._cvt.set_type(_type)

    def get_type(self, name):
        """Gets a tag type as string format.
        
        # Parameters
        name (str):
            Tag name.
        """

        return self._cvt.get_type(name)

    def get_units(self, name):
        """Gets the units defined for a tag.
        
        # Parameters
        name (str):
            Tag name.
        """

        return self._cvt.get_units(name)

    def tag_defined(self, name):
        """Checks if a tag name is already defined.
        
        # Parameters
        name (str):
            Tag name.
        """

        return self._cvt.tag_defined(name)


    def set_tag(self, name, _type, units=""):
        """Sets a new value for a defined tag, in thread-safe mechanism.
        
        # Parameters
        name (str):
            Tag name.
        _type (float, int, bool): 
            Tag value ("int", "float", "bool")
        """
        
        if not self.tag_defined(name):
            self._cvt.set_tag(name, _type, units)

    def set_tags(self, tags):
        """Sets new values for a defined list of tags, 
        in thread-safe mechanism.
        
        # Parameters
        tags (list):
            List of tag name and type.
        """

        for name, _type in tags:
            self.set_tag(name, _type)

    def set_group(self, group, tags):

        self._groups[group] = list()

        for attrs in tags:
            try:
                name, _type, _units = attrs
            except:
                name, _type = attrs
                _units = ""

            self._groups[group].append(name)

            self.set_tag(name, _type, _units)

    def get_group(self, group):

        return self._groups[group]

    def get_groups(self):

        return list(self._groups.keys())

    def get_tags(self):

        return self._cvt.get_tags()

    def write_tag(self, name, value):
        """Writes a new value for a defined tag, in thread-safe mechanism.
        
        # Parameters
        name (str):
            Tag name.
        value (float, int, bool): 
            Tag value ("int", "float", "bool")
        """

        _query = dict()
        _query["action"] = "set_value"

        _query["parameters"] = dict()
        _query["parameters"]["name"] = name
        _query["parameters"]["value"] = value

        self.request(_query)
        result = self.response()

        return result

    def read_tag(self, name):
        """Returns a tag value defined by name, in thread-safe mechanism.
        
        # Parameters
        name (str):
            Tag name.
        """

        _query = dict()
        _query["action"] = "get_value"

        _query["parameters"] = dict()
        _query["parameters"]["name"] = name

        self.request(_query)
        result = self.response()

        if result["result"]:
            return result["response"]

    def read_type(self, name):
        """Returns a tag type defined by name, in thread-safe mechanism.
        
        # Parameters
        name (str):
            Tag name.
        """

        _query = dict()
        _query["action"] = "get_type"

        _query["parameters"] = dict()
        _query["parameters"]["name"] = name

        self.request(_query)
        result = self.response()

        if result["result"]:
            return result["response"]

    def read_units(self, name):
        """Returns the units defined for a tag name, in thread-safe mechanism.
        
        # Parameters
        name (str):
            Tag name.
        """

        _query = dict()
        _query["action"] = "get_units"

        _query["parameters"] = dict()
        _query["parameters"]["name"] = name

        self.request(_query)
        result = self.response()

        if result["result"]:
            return result["response"]

    def request(self, _query):

        self._request_lock.acquire()

        action = _query["action"]

        if action == "set_tag":

            try:
                parameters = _query["parameters"]

                name = parameters["name"]
                _type = parameters["type"]

                self._cvt.set_tag(name, _type)

                self._response = {
                    "result": True
                }
            except Exception as e:
                self._response = {
                    "result": False
                }
        
        elif action == "get_tags":

            try:

                tags = self._cvt.get_tags()

                self._response = {
                    "result": True,
                    "response": tags
                }
            except Exception as e:
                self._response = {
                    "result": False,
                    "response": None
                }

        elif action == "get_value":

            try:

                parameters = _query["parameters"]

                name = parameters["name"]
                value = self._cvt.get_value(name)

                self._response = {
                    "result": True,
                    "response": value
                }
            except Exception as e:
                self._response = {
                    "result": False,
                    "response": None
                }

        elif action == "get_type":

            try:

                parameters = _query["parameters"]

                name = parameters["name"]
                value = self._cvt.get_type(name)

                self._response = {
                    "result": True,
                    "response": value
                }
            except Exception as e:
                self._response = {
                    "result": False,
                    "response": None
                }

        elif action == "get_units":

            try:

                parameters = _query["parameters"]

                name = parameters["name"]
                value = self._cvt.get_units(name)

                self._response = {
                    "result": True,
                    "response": value
                }
            except Exception as e:
                self._response = {
                    "result": False,
                    "response": None
                }

        elif action == "set_value":

            try:

                parameters = _query["parameters"]

                name = parameters["name"]
                value = parameters["value"]
                self._cvt.set_value(name, value)

                self._response = {
                    "result": True
                }
            except Exception as e:
                self._response = {
                    "result": False
                }
        
        elif action in ("attach", "detach"):

            try:
                parameters = _query["parameters"]
                name = parameters["name"]
                observer = parameters["observer"]
                
                if action == "attach":
                    self._cvt.attach_observer(name, observer)
                else:
                    self._cvt.detach_observer(name, observer)

                self._response = {
                    "result": True
                }

            except Exception as e:

                self._response = {
                    "result": False
                }
                
        self._response_lock.release()

    def response(self):

        self._response_lock.acquire()

        result = self._response

        self._request_lock.release()

        return result

    def serialize_tag(self, tag):

        value = self.read_tag(tag)
        _type = self.get_type(tag)
        _units = self.get_units(tag)

        try:
            result = {
                'tag': tag,
                'value': value.serialize(),
                'type': _type,
                'units': _units
            }
        except:
            result = {
                'tag': tag,
                'value': value,
                'type': _type,
                'units': _units
            }

        return result

    def serialize(self):

        result = list()

        tags = self.get_tags()

        for _tag in tags:

            record = self.serialize_tag(_tag)

            result.append(record)

        return result

    def serialize_group(self, name):

        result = list()

        tags = self.get_group(name)

        for _tag in tags:

            record = self.serialize_tag(_tag)

            result.append(record)

        return result

    def __getstate__(self):

        self._response_lock.release()
        state = self.__dict__.copy()
        print(state)
        del state['_request_lock']
        del state['_response_lock']
        return state

    def __setstate__(self, state):
        
        self.__dict__.update(state)
        self._request_lock = threading.Lock()
        self._response_lock = threading.Lock()

        self._response_lock.acquire()
