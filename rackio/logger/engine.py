# -*- coding: utf-8 -*-
"""rackio/logger/engine.py

This module implements a singleton layer above the DataLogger class,
in a thread-safe mode.
"""

import threading

from datetime import datetime

from .data import DataLogger
from .logdict import LogTable
from .._singleton import Singleton


class LoggerEngine(Singleton):
    """Logger Engine class for Tag thread-safe database logging."""

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

                self._response = {"result": True}
            except Exception as e:
                self._response = {"result": False}

        elif action == "read_tag":
            try:
                parameters = _query["parameters"]

                tag = parameters["tag"]

                result = self._logger.read_tag(tag)

                self._response = {"result": True, "response": result}
            except Exception as e:
                self._response = {"result": False, "response": None}

        elif action == "write_event":
            try:
                parameters = _query["parameters"]
                event = parameters["event"]

                self._logger.add_event(event)

                self._response = {"result": True}
            except Exception as e:
                self._response = {"result": False}

        elif action == "read_events":
            try:
                result = self._logger.get_events()

                self._response = {"result": True, "response": result}
            except Exception as e:
                self._response = {"result": False}

        self._response_lock.release()

    def response(self):
        self._response_lock.acquire()

        result = self._response

        self._request_lock.release()

        return result

    def __getstate__(self):
        self._response_lock.release()
        state = self.__dict__.copy()
        del state["_request_lock"]
        del state["_response_lock"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._request_lock = threading.Lock()
        self._response_lock = threading.Lock()

        self._response_lock.acquire()
