# -*- coding: utf-8 -*-
"""rackio/managers/logger.py

This module implements Logger Manager.
"""
import logging

from datetime import datetime

from ..logger import DataLogger
from ..dbmodels import TagTrend, TagValue, Event, Alarm, Blob
from ..utils import serialize_dbo, MemoryTrendValue
from .._singleton import Singleton


class LoggerManager:
    """Logger Manager class for database logging settings.
    """

    def __init__(self, period=0.5, delay=1.0, drop_tables=True, memory_size=None):

        self._period = period
        self._delay = delay
        self._drop_tables = drop_tables

        self._logging_tags = list()
        self._logger = DataLogger()

        self._tables = [TagTrend, TagValue, Event, Alarm, Blob]

        self.set_memory(memory_size)

    def set_db(self, db):

        self._logger.set_db(db)

    def get_db(self):

        return self._logger.get_db()

    def set_dropped(self, drop_tables):

        self._drop_tables = drop_tables

    def get_dropped(self):

        return self._drop_tables

    def set_memory(self, memory):

        self._logger._memory_size = memory
        self.create_memory()
        
    def memory_defined(self):

        if not self._logger._memory_size:
            return False

        return True

    def create_memory(self):

        self._logger.create_memory()

    def write_tag_memory(self, tag, value):

        if not self.memory_defined():
            return

        now = now = datetime.now()
        tag_trend = MemoryTrendValue(value, now)

        try:
            self._memory[tag].append(tag_trend)

            if len(self._memory[tag]) > self._memory_size:
                self._memory[tag].pop(0)
        except:
            self._memory[tag] = [tag_trend]

    def read_tag_memory(self, tag):

        try:
            return self._memory[tag]
        except:
            return None

    def register_table(self, cls):

        self._tables.append(cls)

    def create_tables(self):

        tables = self._tables

        self._logger.create_tables(tables)

        if self.memory_defined():
            self.create_memory()

    def drop_tables(self):

        tables = self._tables
        
        self._logger.drop_tables(tables)

    def add_tag(self, tag):

        self._logging_tags.append(tag)
        self._logging_tags = list(set(self._logging_tags))

    def get_tags(self):

        return self._logging_tags

    def set_tag(self, tag):

        self._logger.set_tag(tag)

    def set_tags(self):

        tags = self.get_tags()
        
        for tag in tags:

            self.set_tag(tag)

    def set_period(self, period):

        self._period = period

    def get_period(self):

        return self._period

    def set_delay(self, delay):

        self._delay = delay

    def get_delay(self):

        return self._delay

    def init_database(self):
    
        if self.get_dropped():
            try:
                self.drop_tables()
            except Exception as e:
                error = str(e)
                logging.error("Database:{}".format(error))

        self.create_tables()

        self.set_tags()

    def summary(self):

        result = dict()

        result["period"] = self.get_period()
        result["tags"] = self.get_tags()
        result["delay"] = self.get_delay()

        return result
    