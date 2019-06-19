# -*- coding: utf-8 -*-
"""rackio/logger.py

This module implements a sqlite database logger for the CVT instance, 
will create a time-serie for each tag in a short memory sqlite data base.
"""

import threading
import pickledb

from datetime import datetime

from ._singleton import Singleton


class TagLogger:

    """CVT Tag Logger class.

    This class is intended to be an API for tags 
    settings and tags logged access.

    # Example
    
    ```python
    >>> from rackio.logger import TagLogger
    >>> _logger = TagLogger()
    ```
    
    """
    
    def __init__(self, dbfile="tags.db", memory=None):

        self._dbfile = dbfile
        self._memory = memory

    def set_dbfile(self, dbfile):

        self._dbfile = dbfile

    def set_db(self):

        self._db = pickledb.load(self._dbfile, False) 

    def set_tag(self, tag):

        self._db.set(tag, list())

    def write_tag(self, tag, value):

        values = self._db.get(tag)
        values.append(value)
        self._db.set(tag, values)
        self._db.dump()

    def read_tag(self, tag):

        result = self._db.get(tag)
        
        return result


class LoggerEngine(Singleton):
    """Logger Engine class for Tag thread-safe database logging.

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

        super(LoggerEngine, self).__init__()

        self._logger = TagLogger()
        self._logging_tags = list()

        self._request_lock = threading.Lock()
        self._response_lock = threading.Lock()

        self._response = None

        self._response_lock.acquire()

    def set_db(self, dbfile):

        self._logger.set_dbfile(dbfile)

    def add_tag(self, tag):

        self._logging_tags.append(tag)

    def write_tag(self, tag, value):

        _query = dict()
        _query["action"] = "write_tag"

        _query["parameters"] = dict()
        _query["parameters"]["tag"] = tag
        _query["parameters"]["value"] = value

        self.request(_query)
        result = self.response()

        return result

    def read_tag(self, tag):

        _query = dict()
        _query["action"] = "read_tag"

        _query["parameters"] = dict()
        _query["parameters"]["tag"] = tag

        self.request(_query)
        result = self.response()

        if result["result"]:
            return result["response"]

    def request(self, _query):

        self._request_lock.acquire()

        action = _query["action"]

        if action == "write_tag":

            try:
                parameters = _query["parameters"]

                tag = parameters["tag"]
                value = parameters["value"]

                self._logger.write_tag(tag, value)

                self._response = {
                    "result": True
                }
            except:
                self._response = {
                    "result": False
                }
        
        elif action == "read_tag":

            try:

                parameters = _query["parameters"]

                tag = parameters["tag"]

                result = self._logger.read_tag(tag)

                self._response = {
                    "result": True,
                    "response": result
                }
            except:
                self._response = {
                    "result": False,
                    "response": None
                }

        self._response_lock.release()

    def response(self):

        self._response_lock.acquire()

        result = self._response

        self._request_lock.release()

        return result
        