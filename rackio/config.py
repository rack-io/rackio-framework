# -*- coding: utf-8 -*-
"""rackio/config.py

This module implements Config class for Rackio configurations handling.
"""
import configparser
import json
import logging
import yaml

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

    def from_yaml(self, config_file):

        with open(config_file) as f:
            c = yaml.load(f)
            
        for key in c.iterkeys():
            if key.isupper():
                self[key] = c[key]

    def from_json(self, config_file):

        with open(config_file) as f:
            data = f.read()

        c = json.loads(data)
            
        for key in c.iterkeys():
            if key.isupper():
                self[key] = c[key]

    def from_ini(self, config_file):

        config = configparser.ConfigParser()
        config.read(config_file)

        for section in config.sections():
            for key, value in config.items(section):
                if key.isupper():
                    self[key] = value

    def update(self, **kwargs):

        for key, value in kwargs:

            try:
                setattr(self, key, value)
            except Exception as e:
                logging.error(e, exc_info=True)

    def __setitem__(self, key, value):
        
        values = {key: value}
        self.update(**values)

    def __getitem__(self, key):
        
        return getattr(self, key)