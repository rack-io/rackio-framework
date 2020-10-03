# -*- coding: utf-8 -*-
"""rackio/config.py

This module implements Config class for Rackio configurations handling.
"""
import logging

from .dbmodels import SQLITE, MYSQL, POSTGRESQL


class RackioConfig:

    # main app settings

    MODE = "development"
    PORT = 8000
    LOGGING_LEVEL = logging.INFO
    LOG_FILE = "app.log"
    MAX_WORKERS = 10

    # db settings

    DBTYPE = SQLITE

    JOURNAL_SIZE_LIMIT = 1024
    CACHE_SIZE = -1024 * 64

    DROP_TABLE = True

    # Logger settings

    LOG_DELAY = 1.0

    # 

    def __init__(self):

        pass

    def update(self, **kwargs):

        for key, value in kwargs:

            try:
                setattr(self, key, value)
            except:
                pass

    def __setitem__(self, key, value):
        
        values = {key: value}
        self.update(**values)

    def __getitem__(self, key):
        
        return getattr(self, key)