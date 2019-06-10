# -*- coding: utf-8 -*-
"""CVT/engine.py

This module implements a Current Value Table (CVT), for holding current
tag values, in a thread safe implementation for Data Acquisition,
Database logging, Math operations and others real time processes.
"""
import threading
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

    def set_tag(self, name, _type):
        """Initialize a new Tag object in the _tags dictionary.
        
        # Parameters
        name (str):
            Tag name.
        _type (str): 
            Tag value type ("int", "float", "bool")
        """
        
        if not _type in ["float", "int", "bool"]:
            raise ValueError
        
        if _type == "float":
            value = 0.0
        elif _type == "int":
            value = 0
        else:
            value = False

        tag = Tag(name, value, _type)

        self._tags[name] = tag

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
        
        if not name in self._tags:
            raise KeyError

        self._tags[name].set_value(value)

    def get_value(self, name):
        """Returns a tag value defined by name.
        
        # Parameters
        name (str):
            Tag name.
        """

        return self._tags[name].get_value()

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
    >>> value = >>> tag_engine.read_tag("TAG1")
    >>> print(value)
    40.43
    ```

    """

    def __init__(self):

        super(CVTEngine, self).__init__()

        self._cvt = CVT()
        self._request_lock = threading.Lock()
        self._response_lock = threading.Lock()

        self._response = None

        self._response_lock.acquire()

    def set_tag(self, name, _type):
        """Sets a new value for a defined tag, in thread-safe mechanism.
        
        # Parameters
        name (str):
            Tag name.
        value (float, int, bool): 
            Tag value ("int", "float", "bool")
        """

        self._cvt.set_tag(name, _type)

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
            except:
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
            except:
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
            except:
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
            except:
                self._response = {
                    "result": False
                }
        
        elif action == "attach":

            try:
                parameters = _query["parameters"]
                name = parameters["name"]
                observer = parameters["observer"]
                
                self._cvt.attach_observer(name, observer)

                self._response = {
                    "result": True
                }

            except:

                self._response = {
                    "result": False
                }

        elif action == "detach":

            try:
                parameters = _query["parameters"]
                name = parameters["name"]
                observer = parameters["observer"]
                
                self._cvt.detach_observer(name, observer)

                self._response = {
                    "result": True
                }

            except:

                self._response = {
                    "result": False
                }

        self._response_lock.release()

    def response(self):

        self._response_lock.acquire()

        result = self._response

        self._request_lock.release()

        return result
