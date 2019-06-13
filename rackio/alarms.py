# -*- coding: utf-8 -*-
"""rackio/models.py

This module implements all Alarms class definitions and Alarm Handlers.
"""
import queue

from .engine import CVTEngine
from .models import TagObserver


class Alarm:

    def __init__(self, name, tag, description):

        self._name = name
        self._tag = tag
        self._description = description

        self._enabled = True
        self._triggered = False
        self._acknowledged = False

        self._state = None
        self._tripped_timestamp = None

    def get_tag(self):

        return self._tag

    def trigger(self):

        self._triggered = True

    def acknowledge(self):

        self._acknowledged = True

    def clear(self):

        self._triggered = False
        
    def reset(self):

        self._enabled = True
        self._triggered = False
        self._acknowledged = False

    def update(self, value):

        pass

    
class AlarmManager:

    def __init__(self):

        self._alarms = list()
        self._tag_queue = queue.Queue()
    
    def append_alarm(self, alarm):

        self._alarms.append(alarm)

    def alarms_tags(self):

        result = [_alarm.get_tag() for _alarm in self._alarms]

        return tuple(result)

    def attach_all(self):

        _cvt = CVTEngine()

        def attach_observers(entity):

            _tag = entity.get_tag()

            observer = TagObserver(self._tag_queue)
            query = dict()
            query["action"] = "attach"
            query["parameters"] = {
                "name": _tag,
                "observer": observer,
            }

            _cvt.request(query)
            _cvt.response()

        for _alarm in self._alarms:

            attach_observers(_alarm)

    def execute(self, tag, value):

        for _alarm in self._alarms:

            if tag == _alarm.get_tag():
                
                _alarm.update(value)
    