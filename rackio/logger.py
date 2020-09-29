# -*- coding: utf-8 -*-
"""rackio/logger.py

This module implements a sqlite database logger for the CVT instance, 
will create a time-serie for each tag in a short memory sqlite data base.
"""

import threading

from datetime import datetime

from .dbmodels import TagTrend, TagValue, Event, Alarm, Blob
from .utils import serialize_dbo, MemoryTrendValue
from ._singleton import Singleton

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class DataLogger:

    """Data Logger class.

    This class is intended to be an API for tags 
    settings and tags logged access.

    # Example
    
    ```python
    >>> from rackio.logger import DataLogger
    >>> _logger = DataLogger()
    ```
    
    """

    def __init__(self):

        self._db = None
        self.tags_dbo = dict()

    def set_db(self, db):

        self._db = db

    def get_db(self):
        
        return self._db

    def set_tag(self, tag, period):

        now = datetime.now()
        trend = TagTrend(name=tag, start=now, period=period)
        trend.save()

        self.tags_dbo[tag] = trend

    def set_tags(self, tags):
        
        for tag in tags:

            self.set_tag(tag)
    
    def create_tables(self, tables):

        if not self._db:
            return
        
        self._db.create_tables(tables, safe=True)

    def drop_tables(self, tables):

        if not self._db:
            return

        self._db.drop_tables(tables)

    def write_tag(self, tag, value):

        trend = self.tags_dbo[tag]

        now = datetime.now()
        tag_value = TagValue.create(tag=trend, value=value, timestamp=now)
        tag_value.save()

    def read_tag(self, tag):
        
        query = TagTrend.select().order_by(TagTrend.start)
        trend = query.where(TagTrend.name == tag).get()
        
        period = trend.period
        values = trend.values.select()
        
        result = dict()

        t0 = values[0].timestamp.strftime('%Y-%m-%d %H:%M:%S')
        values = [value.value for value in values]

        result["t0"] = t0
        result["dt"] = period
        result["values"] = values
        
        return result

    def add_event(self, event):

        event = Event(user=event.user, 
            message=event.message,
            description=event.description,
            classification=event.classification,
            priority=event.priority,
            date_time=event.date_time
        )

        event.save()

    def get_events(self):

        events = Event.select()

        events = [serialize_dbo(event) for event in events]

        return events


class LoggerEngine(Singleton):
    """Logger Engine class for Tag thread-safe database logging.

    """

    def __init__(self):

        super(LoggerEngine, self).__init__()

        self._logger = DataLogger()
        self._logging_tags = list()

        self._request_lock = threading.Lock()
        self._response_lock = threading.Lock()

        self._response = None

        self._response_lock.acquire()

    def set_db(self, db):
    
        self._logger.set_db(db)

    def get_db(self):

        return self._logger.get_db()

    def create_tables(self, tables):

        self._logger.create_tables(tables)

    def drop_tables(self, tables):

        self._logger.drop_tables(tables)

    def set_tag(self, tag, period):

        self._logger.set_tag(tag, period)

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

    def write_event(self, event):

        _query = dict()
        _query["action"] = "write_event"

        _query["parameters"] = dict()
        _query["parameters"]["event"] = event

        self.request(_query)
        result = self.response()

        return result

    def read_events(self):

        _query = dict()
        _query["action"] = "read_events"

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
            except Exception as e:
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
            except Exception as e:
                self._response = {
                    "result": False,
                    "response": None
                }

        elif action == "write_event":

            try:
                
                parameters = _query["parameters"]
                event = parameters["event"]

                self._logger.add_event(event)

                self._response = {
                    "result": True
                }
            except Exception as e:

                self._response = {
                    "result": False
                }

        elif action == "read_events":

            try:

                result = self._logger.get_events()

                self._response = {
                    "result": True,
                    "response": result
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


class QueryLogger:

    def __init__(self):

        self._logger = LoggerEngine()

    def get_values(self, tag):

        query = TagTrend.select().order_by(TagTrend.start.desc())
        trend = query.where(TagTrend.name == tag).get()
        values = trend.values
        
        return values

    def get_period(self, tag):

        query = TagTrend.select().order_by(TagTrend.start.desc())
        trend = query.where(TagTrend.name == tag).get()
        
        return trend.period

    def query(self, tag, start, stop):

        _query = TagTrend.select().order_by(TagTrend.start)
        trend = _query.where(TagTrend.name == tag).get()
        
        start = datetime.strptime(start, DATETIME_FORMAT)
        stop = datetime.strptime(stop, DATETIME_FORMAT)

        period = trend.period
        
        _query = trend.values.select()
        values = _query.where((TagValue.timestamp > start) & (TagValue.timestamp < stop))
        
        result = dict()

        t0 = values[0].timestamp.strftime(DATETIME_FORMAT)
        values = [value.value for value in values]

        result["t0"] = t0
        result["dt"] = period
        
        result["values"] = values

        return result

    def query_last(self, tag, seconds=None, values=None):

        if seconds:

            stop = datetime.now()
            start = stop - seconds

            start = start.strftime(DATETIME_FORMAT)
            stop = stop.strftime(DATETIME_FORMAT)

            return self.query(tag, start, stop)

        if values:

            result = dict()

            tag_values = self.get_values(tag)

            period = self.get_period(tag)

            values *= -1
            
            try:
                tag_values = tag_values[values:]
            except Exception as e:
                tag_values = tag_values[:]

            t0 = tag_values[0].timestamp.strftime(DATETIME_FORMAT)
            tag_values = [value.value for value in tag_values]

            result["t0"] = t0
            result["dt"] = period
        
            result["values"] = tag_values

            return result

    def query_first(self, tag, seconds=None, values=None):

        tag_values = self.get_values(tag)

        if seconds:

            start = tag_values[0].timestamp
            stop = start + seconds

            start = start.strftime(DATETIME_FORMAT)
            stop = stop.strftime(DATETIME_FORMAT)

            return self.query(tag, start, stop)

        if values:

            result = dict()
            
            tag_values = self.get_values(tag)
            
            period = self.get_period(tag)
            t0 = tag_values[0].timestamp.strftime(DATETIME_FORMAT)
            
            tag_values = [value.value for value in tag_values]
            
            try:
                tag_values = tag_values[:values]
            except Exception as e:
                tag_values = tag_values[:]
                
            result["t0"] = t0
            result["dt"] = period
        
            result["values"] = tag_values

            return result
