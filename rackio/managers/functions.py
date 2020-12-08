# -*- coding: utf-8 -*-
"""rackio/managers/functions.py

This module implements Function Manager.
"""
import queue

from ..engine import CVTEngine
from ..models import TagObserver

class FunctionManager:

    def __init__(self):

        self._tags = dict()
        self._tag_queue = queue.Queue()

    def get_queue(self):

        return self._tag_queue

    def append_function(self, tag, function):

        try:
            self._tags[tag].append(function)
        except Exception as e:
            self._tags[tag] = [function]

    def summary(self):

        result = dict()

        length = 0

        for functions in self._tags.values():

            length += len(functions)

        result["length"] = length

        return result

    def attach_all(self):

        engine = CVTEngine()

        for _tag in self._tags:

            observer = TagObserver(self._tag_queue)
            
            engine.attach(_tag, observer)


    def execute(self, tag):

        try:
            for _function in self._tags[tag]:
                _function()
        except Exception as e:
            pass
