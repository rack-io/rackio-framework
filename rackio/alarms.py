# -*- coding: utf-8 -*-
"""rackio/alarms.py

This module implements all Alarms class definitions and Alarm Handlers.
"""
from datetime import datetime

from .engine import CVTEngine
from .events import Event
from .logger import LoggerEngine

NORMAL = "Normal"
UNACKNOWLEDGED = "Unacknowledged"
ACKNOWLEDGED = "Acknowledged"
RTN_UNACKNOWLEDGED = "RTN Unacknowledged"

HI = "HI"
LO = "LO"
BOOL = "BOOL"

USER = "System"


class Alarm:

    tag_engine = CVTEngine()
    logger_engine = LoggerEngine()

    def __init__(self, name, tag, description):

        self._name = name
        self._tag = tag
        self._description = description

        self._trigger_value = None
        self._trigger_type = None  # ["HI", "LO", "BOOL"]
        self._tag_alarm = None

        self._enabled = True       # True: Enable - False: Disable
        
        self._process = True       # True: Normal - False: Abnormal
        self._triggered = False    # True: Active - False: Not Active
        self._acknowledged = True  # True: Acknowledged - False: Unacknowledged

        self._state = NORMAL       # [NORMAL, UNACKNOWLEDGED, ACKNOWLEDGED, RTN_UNACKNOWLEDGED]
        
        self._tripped_timestamp = None
        self._acknowledged_timestamp = None

    def serialize(self):

        result = dict()
        
        result["name"] = self.get_name()
        result["tag"] = self.get_tag()
        result["state"] = self.get_state()
        result["enabled"] = self._enabled
        result["process"] = self._process
        result["triggered"] = self._triggered
        result["acknowledged"] = self._acknowledged

        return result

    def set_trigger(self, value, _type):

        self._trigger_value = value
        self._trigger_type = _type

    def set_tag_alarm(self, tag):

        self._tag_alarm = tag

    def write_tag_alarm(self, value):

        if self._tag_alarm:

            self.tag_engine.write_tag(self._tag_alarm, value)
    
    def get_name(self):

        return self._name

    def get_tag(self):

        return self._tag

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    def get_state(self):

        return self._state

    def set_state(self, _state):

        self._state = _state

        if _state == NORMAL:
            
            self._process = True
            self._triggered = False
            self._acknowledged = True

            message = "Alarm {} back to normal".format(self.get_name())
            priority = 2

            self.write_tag_alarm(False)

        elif _state == UNACKNOWLEDGED:

            self._process = False
            self._triggered = True
            self._acknowledged = False

            message = "Alarm {} triggered".format(self.get_name())
            priority = 1
            
            self.write_tag_alarm(True)

        elif _state == ACKNOWLEDGED:

            self._process = False
            self._triggered = True
            self._acknowledged = True

            message = "Alarm {} has been acknowledged".format(self.get_name())
            priority = 2

            self.write_tag_alarm(True)

        elif _state == RTN_UNACKNOWLEDGED:

            self._process = True
            self._triggered = False
            self._acknowledged = False

            message = "Alarm {} back to normal unacknowledged"
            message = message.format(self.get_name())
            priority = 2

            self.write_tag_alarm(False)

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        description = self._description
        classification = "system"

        event = Event(
            user=USER, 
            message=message,
            description=description,
            classification=classification, 
            priority=priority, 
            date_time=now
        )

        self.logger_engine.write_event(event)

    def trigger(self):

        self._triggered = True        
        self._tripped_timestamp = datetime.now()
        self.set_state(UNACKNOWLEDGED)

    def disable(self):

        self._enabled = False

    def enable(self):

        self._enabled = True

    def acknowledge(self):

        if self._state == UNACKNOWLEDGED:

            self.set_state(ACKNOWLEDGED)
        
        if self._state == RTN_UNACKNOWLEDGED:
            
            self.set_state(NORMAL)

        self._acknowledged_timestamp = datetime.now()

    def clear(self):

        self._triggered = False

        if self._tag_alarm:

            self.tag_engine.write_tag(self._tag_alarm, False)
        
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

        if _state in (NORMAL, RTN_UNACKNOWLEDGED):

            if _type == HI and value >= self._trigger_value:
                self.trigger()

            elif _type == LO and value <= self._trigger_value:
                self.trigger()

            elif _type == BOOL and value:
                self.trigger()

        elif _state == UNACKNOWLEDGED:

            if _type == HI and value < self._trigger_value:
                self.set_state(RTN_UNACKNOWLEDGED)

            elif _type == LO and value > self._trigger_value:
                self.set_state(RTN_UNACKNOWLEDGED)

            elif _type == BOOL and not value:
                self.set_state(RTN_UNACKNOWLEDGED)

        elif _state == ACKNOWLEDGED:

            if _type == HI and value < self._trigger_value:
                self.set_state(NORMAL)

            elif _type == LO and value > self._trigger_value:
                self.set_state(NORMAL)

            elif _type == BOOL and not value:
                self.set_state(NORMAL)
