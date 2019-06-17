# -*- coding: utf-8 -*-
"""rackio/logger.py

This module implements a sqlite database logger for the CVT instance, 
will create a time-serie for each tag in a short memory sqlite data base.
"""

import threading
import pickledb

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

        self._dbfile = pickledb.load(dbfile, False)
        self._memory = memory

    def set_tag(self, tag):

        self._dbfile.set(tag, list())

    def write_tag(self, tag, value):

        values = self._dbfile.get(tag)
        values.append(value)
        self._dbfile.set(tag, values)
        self._dbfile.dump()

    def read_tag(self, tag):

        result = self._dbfile.get(tag)
        
        return result


class LoggerEngine:
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

    def __init__(self, dbfile):

        # super(LoggerEngine, self).__init__()

        self._logger = TagLogger(dbfile)
        self._logging_tags = list()

        self._response = None

    def add_tag(self, tag):

        self._logging_tags.append(tag)
        