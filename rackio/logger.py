# -*- coding: utf-8 -*-
"""rackio/logger.py

This module implements a sqlite database logger for the CVT instance, 
will create a time-serie for each tag in a short memory sqlite data base.
"""

import threading

from sqlitedict import SqliteDict
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
    
    def __init__(self, dbfile, memory=None):

        self._dbfile = dbfile
        self._memory = memory
        
        with SqliteDict(self._dbfile) as _sqlitedb:
            
            _sqlitedb["tags"] = dict()

    def set_tag(self, tag):

        with SqliteDict(self._dbfile) as _sqlitedb:

            _sqlitedb["tags"][tag] = list()

    def write_tag(self, tag, value):

        with SqliteDict(self._dbfile) as _sqlitedb:

            now = datetime.now()

            _value = (now, value,)

            _sqlitedb["tags"][tag].append(_value)
            _sqlitedb.commit()

    def read_tag(self, tag):

        with SqliteDict(self._dbfile) as _sqlitedb:

            result = _sqlitedb["tags"][tag]
            _sqlitedb.commit()

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
    >>> value = >>> tag_engine.read_tag("TAG1")
    >>> print(value)
    40.43
    ```

    """

    def __init__(self, dbfile):

        super(LoggerEngine, self).__init__()

        self._logger = TagLogger(dbfile)
        self._request_lock = threading.Lock()
        self._response_lock = threading.Lock()

        self._response = None

        self._response_lock.acquire()

        