# -*- coding: utf-8 -*-
"""rackio/models.py

This module implements all Alarms class definitions and Alarm Handlers.
"""
import queue

from datetime import datetime

from .engine import CVTEngine
from .models import TagObserver


class Alarm:

    def __init__(self, name, tag, description):

        self._name = name
        self._tag = tag
        self._description = description

        self._trigger_value = None
        self._trigger_type = None       # ["HI", "LO", "BOOL"]

        self._enabled = True            # True: Enable       - False: Disable
        
        self._process = True            # True: Normal       - False: Abnormal
        self._triggered = False         # True: Active       - False: Not Active
        self._acknowledged = True       # True: Acknowledged - False: Unacknowledged

        self._state = "Normal"          # ["Normal", "Unacknowledged", "Acknowledged", "RTN Unacknowledged"]
        
        self._tripped_timestamp = None
        self._acknowledged_timestamp = None

    def serialize(self):

        result = dict()
        
        result["name"] = self._name
        result["state"] = self._state
        result["enabled"] = self._enabled
        result["process"] = self._process
        result["triggered"] = self._triggered
        result["acknowledged"] = self._acknowledged

        return result

    def set_trigger(self, value, _type):

        self._trigger_value = value
        self._trigger_type = _type
    
    def get_name(self):

        return self._name

    def get_tag(self):

        return self._tag

    def get_state(self):

        return self._state

    def set_state(self, _state):

        self._state = _state

        if _state == "Normal":

            self._process = True
            self._triggered = False
            self._acknowledged = True

        elif _state == "Unacknowledged":

            self._process = False
            self._triggered = True
            self._acknowledged = False

        elif _state == "Acknowledged":

            self._process = False
            self._triggered = True
            self._acknowledged = True

        elif _state == "RTN Unacknowledged":

            self._process = True
            self._triggered = False
            self._acknowledged = False

    def trigger(self):

        self._triggered = True
        self._tripped_timestamp = datetime.now()

    def disable(self):

        self._enabled = False

    def enable(self):

        self._enabled = True

    def acknowledge(self):

        if self._state == "Unacknowledged":

            self.set_state("Acknowledged")
        
        if self._state == "RTN Unacknowledged":
            
            self.set_state("Normal")

        self._acknowledged_timestamp = datetime.now()

    def clear(self):

        self._triggered = False
        
    def reset(self):

        self._enabled = True
        self._triggered = False
        self._acknowledged = False

        self._tripped_timestamp = None
        self._acknowledged_timestamp = None

    def update(self, value):

        if not self._enabled:
            return

        _state = self._state
        _type = self._trigger_type

        if _state == "Normal" or _state == "RTN Unacknowledged":

            if _type == "HI":

                if value >= self._trigger_value:
                    self.set_state("Unacknowledged")

            elif _type == "LO":

                if value <= self._trigger_value:
                    self.set_state("Unacknowledged")

            elif _type == "BOOL":

                if value:
                    self.set_state("Unacknowledged")

        elif _state == "Unacknowledged":

            if _type == "HI":

                if value < self._trigger_value:
                    self.set_state("RTN Unacknowledged")

            elif _type == "LO":

                if value > self._trigger_value:
                    self.set_state("RTN Unacknowledged")

            elif _type == "BOOL":

                if not value:
                    self.set_state("RTN Unacknowledged")

        elif _state == "Acknowledged":

            if _type == "HI":

                if value < self._trigger_value:
                    self.set_state("Normal")

            elif _type == "LO":

                if value > self._trigger_value:
                    self.set_state("Normal")

            elif _type == "BOOL":

                if not value:
                    self.set_state("Normal")


class AlarmManager:

    def __init__(self):

        self._alarms = list()
        self._tag_queue = queue.Queue()
    
    def append_alarm(self, alarm):

        self._alarms.append(alarm)

    def get_alarm(self, name):

        for _alarm in self._alarms:
            if name == _alarm.get_name():
                return _alarm

    def get_alarms(self):

        result = list()

        for _alarm in self._alarms:
            result.append(_alarm)

        return result

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

    def execute(self, tag):

        _cvt = CVTEngine()
        value = _cvt.read_tag(tag)

        for _alarm in self._alarms:

            if tag == _alarm.get_tag():

                _alarm.update(value)
    