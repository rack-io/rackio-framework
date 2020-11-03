# -*- coding: utf-8 -*-
"""rackio/state.py

This module implements all state machine classes.
"""
import sys
import linecache
import logging

from inspect import ismethod

from statemachine import StateMachine, State

from .models import FloatType, IntegerType, BooleanType, StringType

from .engine import CVTEngine
from .logger import QueryLogger, LoggerEngine
from .utils import log_detailed

FLOAT = "float"
INTEGER = "int"
BOOL = "bool"
STRING = "str"

READ = "read"
WRITE = "write"

def detailed_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    message =  'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

    return message


class TagBinding:

    """
    Class used within Rackio State Machine.

    This class is used to bind tag values with 
    an instance of a Rackio State Machine object,
    in the machine loop, before executing current
    state, tag bindings of an object are updated
    with last values from the Tag Engine, 
    after execution, the Tag Engine is updated,
    the direction of the binding must be provided, 
    otherwise `read` direction is used.

    Usage:

    ```python
    class TwoStep(RackioStateMachine):

        # states

        state1  = State('State1', initial=True)
        state2  = State('State2')

        # transitions
    
        forward = state1.to(state2)
        back = state2.to(state1)

        # bindings

        t1 = TagBinding("T1")
        t2 = TagBinding("T2", direction="write")
    ```
    """

    tag_engine = CVTEngine()

    def __init__(self, tag, direction="read"):
        
        self.tag = tag
        self.direction = direction
        self.value = None

    def update(self):

        if self.direction == WRITE:

            self.tag_engine.write_tag(self.tag, self.value)

        if self.direction == READ:

            self.value = self.tag_engine.read_tag(self.tag)

class Group:

    pass


class GroupBinding:

    """
    Class used within Rackio State Machine.

    This class is used to bind a tag group values 
    with an instance of a Rackio State Machine object,
    in the machine loop, before executing current
    state, group bindings of an object are updated
    with last values of all tags in that group from 
    the Tag Engine, after execution, the Tag Engine 
    is updated, the direction of the binding must be 
    provided, otherwise `read` direction is used.

    Usage:

    ```python
    class TwoStep(RackioStateMachine):

        # states

        state1  = State('State1', initial=True)
        state2  = State('State2')

        # transitions
    
        forward = state1.to(state2)
        back = state2.to(state1)

        # bindings

        g1 = GroupBinding("G1")
        g2 = GroupBinding("G2", direction="write")
    ```
    """
    
    tag_engine = CVTEngine()

    def __init__(self, group, direction="read"):
        
        self.group = group
        self.direction = direction
        self.values = Group()

        self.tags = self.tag_engine.get_group(self.group)

        self._init_group()

    def _init_group(self):

        for tag in self.tags:
            tag_value = self.tag_engine.read_tag(tag)
            setattr(self.values, tag, tag_value)

    def update(self):

        for tag in self.tags:

            if self.direction == WRITE:

                value = getattr(self.values, tag)

                self.tag_engine.write_tag(tag, value)

            if self.direction == READ:

                value = self.tag_engine.read_tag(tag)

                setattr(self.values, tag, value)
    

class RackioStateMachine(StateMachine):

    """
    Class used to define custom state machines.

    This class is used to define custom machines,
    by defining parameters, states, transitions and 
    by defining methods state behaviour can de defined.

    **Parameters:**
        
    * **name** (str): state machine name.

    Usage:

    ```python
    from rackio import RackioStateMachine, State

    
    class TwoStep(RackioStateMachine):

        # states

        state1  = State('State1', initial=True)
        state2  = State('State2')

        # transitions
    
        forward = state1.to(state2)
        back = state2.to(state1)

        # parameters

        count = 0

        def on_back(self):

            self.count = 0

        def while_state1(self):

            self.count += 1

            logging.warning("{}: {}".format(self.name, self.count))
            if self.count == 5:
                self.forward()

        def while_state2(self):

            self.count += 1

            logging.warning("{}: {}".format(self.name, self.count))
            if self.count >= 10:
                self.back()
    ```
    """

    tag_engine = CVTEngine()
    logger_engine = LoggerEngine()
    query_logger = QueryLogger()

    def __init__(self, name, **kwargs):
        
        super(RackioStateMachine, self).__init__()
        self.name = name
        self._tag_bindings = list()
        self._group_bindings = list()

        attrs = self.get_attributes()

        for key, value in attrs.items():

            try:

                if isinstance(value, TagBinding):
                    self._tag_bindings.append((key, value))
                    _value = self.tag_engine.read_tag(value.tag)

                    setattr(self, key, _value)

                if isinstance(value, GroupBinding):
                    self._group_bindings.append((key, value))
                    _value = value.values

                    setattr(self, key, _value)

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
            except Exception as e:
                continue

        self.attrs = attrs
    
    def get_states(self):

        return [state.identifier for state in self.states]
    
    @classmethod
    def get_attributes(cls):

        result = dict()
        
        props = cls.__dict__

        for key, value in props.items():

            if key in ["states", "transitions", "states_map", "_loop", "get_attributes", "_tag_bindings"]:
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

    def _update_tags(self, direction=READ):

        for attr, _binding in self._tag_bindings:

            try:
                if direction == READ and _binding.direction == READ:
                
                    tag = _binding.tag
                    value = self.tag_engine.read_tag(tag)
                    value = setattr(self, attr, value)
                
                elif direction == WRITE and _binding.direction == WRITE:
                    tag = _binding.tag
                    value = getattr(self, attr)
                    self.tag_engine.write_tag(tag, value)
            
            except Exception as e:
                message = "Machine - {}: Error on machine tag-bindings".format(self.name)
                log_detailed(e, message)

    def _update_groups(self, direction=READ):
    
        for attr, _binding in self._group_bindings:

            try:
                if direction == READ and _binding.direction == READ:
                
                    _binding.update()

                    setattr(self, attr, _binding.values)
                
                elif direction == WRITE and _binding.direction == WRITE:
                    
                    values = getattr(self, attr)
                    
                    _binding.values = values

                    _binding.update()
            
            except Exception as e:
                message = "Machine - {}: Error on machine group-bindings".format(self.name)
                log_detailed(e, message)

    def _loop(self):

        try:
            state_name = self.current_state.identifier.lower()
            method_name = "while_" + state_name

            if method_name in dir(self):
                update_tags = getattr(self, '_update_tags')
                update_groups = getattr(self, '_update_groups')
                method = getattr(self, method_name)
                
                # update tag read bindings
                update_tags()
                update_groups()

                # loop machine
                try:
                    method()
                except Exception as e:
                    message = "Machine - {}: Error on machine loop".format(self.name)
                    log_detailed(e, message)

                #update tag write bindings
                update_tags("write")
                update_groups("write")

        except Exception as e:
            error = str(e)
            logging.error("Machine - {}:{}".format(self.name, error))

    def loop(self):

        self._loop()
    
    def serialize(self):

        def is_serializable(value):

            if isinstance(value, float):
                return True

            if isinstance(value, int):
                return True

            if isinstance(value, bool):
                return True

            if isinstance(value, str):
                return True

            return False

        def ismodel_instance(obj):

            for cls in [FloatType, IntegerType, BooleanType, StringType]:
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

            if not is_serializable(value):
                try:
                    obj = attrs[key]

                    if isinstance(obj, FloatType):
                        value = float(value)
                    elif isinstance(obj, IntegerType):
                        value = int(value)
                    elif isinstance(obj, BooleanType):
                        value = bool(value)
                    else:
                        value = str(value)

                except Exception as e:
                    
                    error = str(e)

                    logging.error("Machine - {}:{}".format(self.name, error))
                    value = None

            result[key] = value

        return result
        