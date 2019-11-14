# -*- coding: utf-8 -*-
"""rackio/state.py

This module implements all state machine classes.
"""
from inspect import ismethod

from statemachine import StateMachine, State

from .models import FloatField, IntegerField, BooleanField, StringField

from .engine import CVTEngine
from .logger import QueryLogger, LoggerEngine

FLOAT = "float"
INTEGER = "int"
BOOL = "bool"
STRING = "str"


class RackioStateMachine(StateMachine):

    tag_engine = CVTEngine()
    logger_engine = LoggerEngine()
    query_logger = QueryLogger()

    def __init__(self, name, **kwargs):
        
        super(RackioStateMachine, self).__init__()
        self.name = name

        attrs = self.get_attributes()

        for key, value in attrs.items():

            try:
                if key in kwargs:
                    default = kwargs[key]
                else:
                    default = value.default
                    _type = value._type

                if default:
                    setattr(self, key, default)
                else:
                    if _type == FLOAT:
                        setattr(self, key, 0.0)
                    elif _type == INTEGER:
                        setattr(self, key, 0)
                    elif _type == BOOL:
                        setattr(self, key, False)
                    elif _type == STRING:
                        setattr(self, key, "")
            except:
                continue

        self.attrs = attrs
    
    def get_states(self):

        return [state.identifier for state in self.states]
    
    @classmethod
    def get_attributes(cls):

        result = dict()
        
        props = cls.__dict__

        for key, value in props.items():

            if key in ["states", "transitions", "states_map", "get_attributes"]:
                continue
            if hasattr(value, '__call__'):
                continue
            if isinstance(value, cls):
                continue
            if isinstance(value, State):
                continue
            if not ismethod(value):

                if not "__" in key:
                    result[key] = value

        return result
    
    def serialize(self):

        def ismodel_instance(obj):

            for cls in [FloatField, IntegerField, BooleanField, StringField]:
                if isinstance(obj, cls):
                    return True
            return False

        result = dict()

        result["state"] = self.current_state.identifier

        states = self.get_states()
        checkers = ["is_" + state for state in states]
        methods = ["while_" + state for state in states]

        attrs = self.get_attributes()
        
        for key in attrs.keys():
            if key in checkers:
                continue
            if key in methods:
                continue
            if not ismodel_instance(attrs[key]):
                continue
            value = getattr(self, key)
            result[key] = value

        return result


class StateMachineManager:

    def __init__(self):

        self._machines = list()

    def append_machine(self, machine, interval=1):
        
        self._machines.append((machine, interval,))

    def get_machines(self):

        result = [_machine for _machine in self._machines]
        
        return result

    def get_machine(self, name):

        for _machine, interval in self._machines:

            if name == _machine.name:

                return _machine

    def start_machine(self, name):

        for _machine, interval in self._machines:

            if name == _machine.name:

                _machine.start()
                break

