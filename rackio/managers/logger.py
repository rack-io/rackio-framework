# -*- coding: utf-8 -*-
"""rackio/managers/logger.py

This module implements Logger Manager.
"""
import logging

from datetime import datetime

from ..logger import LogTable, LoggerEngine
from ..dbmodels import TagTrend, TagValue, Event, Alarm, Blob
from ..dbmodels import UserRole, User, Authentication, License, Systems
from ..utils import serialize_dbo
from .._singleton import Singleton

from .auth import AuthManager


class LoggerManager:
    """Logger Manager class for database logging settings.
    """

    def __init__(self, period=0.5, delay=1.0, drop_tables=True):

        self._period = period
        self._delay = delay
        self._drop_tables = drop_tables

        self._logging_tags = LogTable()
        self._logger = LoggerEngine()
        self._auth = AuthManager()

        self._tables = [TagTrend, TagValue, Event, Alarm, Blob]
        self._tables += [UserRole, User, Authentication, License, Systems]

    def set_db(self, db):

        self._logger.set_db(db)

    def get_db(self):

        return self._logger.get_db()

    def set_dropped(self, drop_tables):

        self._drop_tables = drop_tables

    def get_dropped(self):

        return self._drop_tables

    def register_table(self, cls):

        self._tables.append(cls)

    def create_tables(self):

        tables = self._tables

        self._logger.create_tables(tables)

    def drop_tables(self):

        tables = self._tables
        
        self._logger.drop_tables(tables)

    def add_tag(self, tag, period):
        
        self._logging_tags.add_tag(tag, period)

    def get_tags(self):

        return self._logging_tags.get_all_tags()

    def set_tag(self, tag, period):

        self._logger.set_tag(tag, period)

    def set_tags(self):

        for period in self._logging_tags.get_groups():
            
            tags = self._logging_tags.get_tags(period)
        
            for tag in tags:

                self.set_tag(tag, period)

    def get_table(self):

        return self._logging_tags
        
    def set_period(self, period):

        self._period = period

    def get_period(self):

        return self._period

    def set_delay(self, delay):

        self._delay = delay

    def get_delay(self):

        return self._delay

    def set_root(self, username, password):
        
        self._auth.set_root(username, password)

    def create_user(self, username, password, role, lic):

        self._auth.create_user(username, password, role, lic)

    def create_role(self, role):

        self._auth.create_role(role)

    def create_system(self, system):

        self._auth.create_system(system)

    def init_database(self):
    
        if self.get_dropped():
            try:
                self.drop_tables()
            except Exception as e:
                error = str(e)
                logging.error("Database:{}".format(error))

        self.create_tables()

        self.set_tags()

        self._auth.init()

    def summary(self):

        result = dict()

        result["period"] = self.get_period()
        result["tags"] = self.get_tags()
        result["delay"] = self.get_delay()

        return result
    