# -*- coding: utf-8 -*-
"""rackio/alarms.py

This module implements all Alarms class definitions and Alarm Handlers.
"""
from datetime import datetime

from .engine import CVTEngine
from .events import Event
from .dbmodels import Alarm as AlarmModel
from .dbmodels import AlarmSummary
from .logger import LoggerEngine

NORMAL = "Normal"
UNACKNOWLEDGED = "Unacknowledged"
ACKNOWLEDGED = "Acknowledged"
RTN_UNACKNOWLEDGED = "RTN Unacknowledged"
SHELVED = "Shelved"
SUPRESSED_BY_DESIGN = "Supressed By Design"
OUT_OF_SERVICE = "Out Of Service"

HH = "HI - HI"
HI = "HI"
LO = "LO"
LL = "LO - LO"
BOOL = "BOOL"

USER = "System"


class Alarm:

    tag_engine = CVTEngine()
    logger_engine = LoggerEngine()

    def __init__(self, name, tag, description):

        self._name = name
        self._tag = tag
        self._description = description

        self._value = None

        self._trigger_value = None
        self._trigger_type = None  # ["HH", "HI", "LO", "LL", "BOOL"]
        self._tag_alarm = None

        self._enabled = True       # True: Enable - False: Disable (Out Of Service)
        
        self._process = True       # True: Normal - False: Abnormal
        self._triggered = False    # True: Active - False: Not Active
        self._acknowledged = True  # True: Acknowledged - False: Unacknowledged

        self._state = NORMAL       # [NORMAL, UNACKNOWLEDGED, ACKNOWLEDGED, RTN_UNACKNOWLEDGED, SHELVED, SUPPRESSED_BY_DESIGN, OUT_OF_SERVICE]
        
        self._tripped_timestamp = None
        self._acknowledged_timestamp = None
        self._silence = False
        self._shelved = False
        self._supressed_by_design = False
        self._out_of_service = False

        self._by_confirm_reset = False

    def serialize(self):

        result = dict()
        
        result["name"] = self.get_name()
        result["tag"] = self.get_tag()
        result["tag_alarm"] = self._tag_alarm
        result["state"] = self.get_state()
        result["enabled"] = self._enabled
        result["process"] = self._process
        result["triggered"] = self._triggered
        result["acknowledged"] = self._acknowledged
        result["value"] = self._value
        result["tripped_value"] = self._trigger_value
        result["tripped_timestamp"] = self._tripped_timestamp
        result["acknowledged_timestamp"] = self._acknowledged_timestamp
        result["type"] = self._trigger_type
        result["silence"] = self._silence
        result["by_confirm_reset"] = self._by_confirm_reset
        result["shelved"] = self._shelved
        result["supressed_by_design"] = self._supressed_by_design
        result["out_of_service"] = self._out_of_service
        result["description"] = self.description

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
            self._tripped_timestamp = None
            self._acknowledged_timestamp = None

            message = "Alarm {} back to normal".format(self.get_name())
            priority = 2
            classification = "system"
            self.write_tag_alarm(False)

        elif _state == UNACKNOWLEDGED:

            self._process = False
            self._triggered = True
            self._acknowledged = False
            self._acknowledged_timestamp = None

            message = "{}".format(self.description)
            priority = 1
            classification = "system"
            self.write_tag_alarm(True)

            AlarmSummary.create(
                name=self.get_name(), 
                state=_state,
                alarm_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                description=message,
                classification=classification, 
                priority=priority
            )

        elif _state == ACKNOWLEDGED:

            self._process = False
            self._triggered = True
            self._acknowledged = True

            message = "Alarm {} has been acknowledged".format(self.get_name())
            priority = 2
            classification = "user"
            self.write_tag_alarm(True)
            alarm_summary = AlarmSummary.select().where(AlarmSummary.name == self.get_name()).order_by(AlarmSummary.id.desc()).get()
            now = datetime.now()
            alarm_summary = AlarmSummary.update(
                {
                    AlarmSummary.ack_time: now.strftime("%Y/%m/%d %H:%M:%S"),
                    AlarmSummary.state: ACKNOWLEDGED
                }
            ).where(AlarmSummary.id == alarm_summary)
            alarm_summary.execute()

        elif _state == RTN_UNACKNOWLEDGED:

            self._process = True
            self._triggered = False
            self._acknowledged = False

            message = "Alarm {} returned to normal unacknowledged".format(self.get_name())
            priority = 2
            classification = "system"
            self.write_tag_alarm(False)
            alarm_summary = AlarmSummary.select().where(AlarmSummary.name == self.get_name()).order_by(AlarmSummary.id.desc()).get()
            alarm_summary = AlarmSummary.update(
                {
                    AlarmSummary.state: RTN_UNACKNOWLEDGED
                }
            ).where(AlarmSummary.id == alarm_summary)
            alarm_summary.execute()

        elif _state == SHELVED:

            self._process = None
            self._triggered = None
            self._acknowledged = None

            message = "Alarm {} shelved".format(self.get_name())
            priority = 3
            classification = "user"
            self.write_tag_alarm(False)

        elif _state == SUPRESSED_BY_DESIGN:

            self._process = None
            self._triggered = None
            self._acknowledged = None

            message = "Alarm {} supressed by design".format(self.get_name())
            priority = 3
            classification = "user"
            self.write_tag_alarm(False)

        elif _state == OUT_OF_SERVICE:

            self._process = None
            self._triggered = None
            self._acknowledged = None

            message = "Alarm {} out of service".format(self.get_name())
            priority = 3
            classification = "user"

            self.write_tag_alarm(False)

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        description = self._description
        
        AlarmModel.create(
            user=USER, 
            message=message,
            description=description,
            classification=classification, 
            priority=priority, 
            date_time=now,
            name=self.get_name(),
            state=self.get_state()
        )

    def trigger(self):

        if not self._enabled:

            return

        elif self._out_of_service:

            return

        elif self._supressed_by_design:

            return

        elif self._shelved:

            return
            
        self._triggered = True        
        self._tripped_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.set_state(UNACKNOWLEDGED)

    def disable(self):

        self._enabled = False

    def enable(self):

        self._enabled = True

    def acknowledge(self):

        if not self._enabled:

            return

        if self._state == UNACKNOWLEDGED:

            self.set_state(ACKNOWLEDGED)
        
        if self._state == RTN_UNACKNOWLEDGED:
            
            self.set_state(NORMAL)

        self._acknowledged_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def silence(self):

        if not self._enabled:

            return

        self._silence = True

    def sound(self):

        if not self._enabled:

            return
        
        self._silence = False

    def clear(self):

        if not self._enabled:

            return

        self._triggered = False

        if self._tag_alarm:

            self.tag_engine.write_tag(self._tag_alarm, False)
        
    def reset(self):

        self._enabled = True
        self._triggered = False
        self._acknowledged = False
        self._tripped_timestamp = None
        self._acknowledged_timestamp = None
        self._silence = False
        self._by_confirm_reset = False
        self._shelved = False
        self._out_of_service = False
        self._supressed_by_design = False

        self.set_state(NORMAL)

    def shelve(self):

        self._shelved = True
        self.set_state(SHELVED)

    def unshelve(self):

        self._shelved = False
        self.set_state(NORMAL)

    def supress_by_design(self):

        self._supressed_by_design = True
        self.set_state(SUPRESSED_BY_DESIGN)

    def unsupress_by_design(self):

        self._supressed_by_design = False
        self.set_state(NORMAL)

    def out_of_service(self):

        self._out_of_service = True
        self.set_state(OUT_OF_SERVICE)
    
    def in_service(self):

        self._out_of_service = False
        self.set_state(NORMAL)

    def confirm_reset(self):

        self.reset()

    def to_reset(self):

        self._by_confirm_reset = True

    def update(self, value):

        self._value = value

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

