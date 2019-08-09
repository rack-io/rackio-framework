# -*- coding: utf-8 -*-
"""rackio/state.py

This module implements all state machine classes.
"""
from inspect import ismethod

from statemachine import StateMachine, State

FLOAT = "float"
INTEGER = "int"
BOOL = "bool"
STRING = "str"


class RackioStateMachine(StateMachine):

    def __init__(self, name):
        
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

        return [s.identifier for s in self.states]
    
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

        result = dict()

        result["state"] = self.current_state.name

        states = self.get_states()
        checkers = ["is_" + state for state in states]
        methods = ["while_" + state for state in states]

        attrs = self.get_attributes()
        
        for key in attrs.keys():
            if key in checkers:
                continue
            if key in methods:
                continue
            value = getattr(self, key)
            result[key] = value

        return result


class StateMachineManager:

    def __init__(self):

        self._machines = list()

    def append_machine(self, machine):
        
        self._machines.append(machine)

    def get_machine(self, name):

        for _machine in self._machines:

            if name == _machine.name:

                return _machine

