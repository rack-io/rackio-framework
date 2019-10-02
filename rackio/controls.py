# -*- coding: utf-8 -*-
"""rackio/models.py

This module implements a Controls classes for taking
actions into Tags oberservers.
"""
import queue

from threading import Thread

from pybigparser.evaluator import get_vars, MathParser

from .engine import CVTEngine
from .models import TagObserver


class ValueAction:

    """ValueAction class.

    This class defines a mechanism to apply defined values
    as actions on tags values

    # Example
    
    ```python
    >>> from rackio.controls import ValueAction
    >>> act1 = ValueAction("T3", 40)
    ```

    # Parameters
    tag_name (str):
        tag name in which action will occur
    value (int, float, bool):
        Value to be assigned once the action is executed
    
    """

    def __init__(self, tag_name, value):

        self.tag_name = tag_name
        self.value = value

    def serialize(self):

        result = dict()
        
        result["type"] = "ValueAction"
        result["tag"] = self.tag_name
        result["value"] = self.value

        return result

    def trigger(self):

        _cvt = CVTEngine()

        name = self.tag_name
        value = self.value

        query = dict()
        query["action"] = "set_value"
        query["parameters"] = dict()
        
        query["parameters"]["name"] = name
        query["parameters"]["value"] = value
        
        _cvt.request(query)
        _cvt.response()


class MathAction:

    """MathAction class.

    This class defines a mechanism to apply 
    mathematical expressions as actions on 
    tags values

    # Example
    
    ```python
    >>> from rackio.controls import MathAction
    >>> act1 = MathAction("T3", "T1 + 2 * T2")
    ```

    # Parameters
    tag_name (str):
        tag name in which action will occur
    expression (str):
        Mathematical expression to be parsed once the action is executed
    
    """

    def __init__(self, tag_name, expression):

        self.tag_name = tag_name
        self._expression = expression

        self._parser = MathParser()
        self._parser.set_function(self._expression)

    def serialize(self):

        result = dict()
        
        result["type"] = "MathAction"
        result["tag"] = self.tag_name
        result["expresion"] = self._expression

        return result

    def trigger(self):

        _cvt = CVTEngine()

        name = self.tag_name
        
        tags = get_vars(self._expression)

        values = [_cvt.read_tag(tag) for tag in tags]

        for tag, value in zip(tags, values):

            self._parser.add_sub(tag, value)

        _value = self._parser.evaluate()

        _cvt.write_tag(name, _value)


class Condition:

    """Condition class.

    This class defines a mechanism to apply conditions
    on tags values

    # Example
    
    ```python
    >>> from rackio.controls import Condition
    >>> cond1 = Condition("T1",">=", "T2")
    ```

    # Parameters
    tag1 (str):
        First tag name to be compared
    _oper (str):
        Comparison operators ("=", "!=", "<", ">", "<=", ">=")
    tag2 (str):
        Second tag name to be compared
    
    """

    def __init__(self, tag1, _oper, tag2):

        self.tag1 = tag1
        self._oper = _oper
        self.tag2 = tag2

    def tags(self):

        return (self.tag1, self.tag2)

    def serialize(self):

        result = dict()

        result["type"] = "Condition"
        result["left"] = self.tag1
        result["right"] = self.tag2
        result["relation"] = self._oper

        return result

    def evaluate(self):

        _oper = self._oper

        _cvt = CVTEngine()

        _cvt.request({
            "action": "get_value",
            "parameters": {
                "name": self.tag1,
            }
        })
    
        response = _cvt.response()
        if not response["result"]:
            raise KeyError
        
        value1 = response["response"]

        _cvt.request({
            "action": "get_value",
            "parameters": {
                "name": self.tag2,
            }
        })
    
        response = _cvt.response()
        if not response["result"]:
            raise KeyError
        
        value2 = response["response"]

        if _oper == "=":

            return value1 == value2
        
        elif _oper == "<":

            return value1 < value2

        elif _oper == "<=":

            return value1 <= value2

        elif _oper == ">":

            return value1 > value2

        elif _oper == ">=":

            return value1 >= value2

        else:
            return False


class OrCondition:

    """Condition class.

    This class defines a mechanism to apply conditions
    on tags values

    # Example
    
    ```python
    >>> from rackio.controls import Condition, OrCondition
    >>> cond1 = Condition("T1",">=", "T2")
    >>> cond2 = Condition("T4","<=", "T5")
    >>> cond3 = OrCondition([cond1, cond2])
    ```

    # Parameters
    conditions (list):
        List of other condition objects

    """

    def __init__(self, conditions):

        self._conditions = conditions

    def tags(self):

        result = tuple()

        for _condition in self._conditions:
            result += _condition.tags()

        return result

    def serialize(self):

        result = dict()
        result["type"] = "OrCondition"
        result["conditions"] = [_condition.serialize() for _condition in self._conditions]

        return result

    def evaluate(self):

        result = False

        for _condition in self._conditions:

            result = result or _condition.evaluate()

        return tuple(set(result))


class AndCondition:

    """Condition class.

    This class defines a mechanism to apply conditions
    on tags values

    # Example
    
    ```python
    >>> from rackio.controls import Condition, AndCondition
    >>> cond1 = Condition("T1",">=", "T2")
    >>> cond2 = Condition("T4","<=", "T5")
    >>> cond3 = AndCondition([cond1, cond2])
    ```

    # Parameters
    conditions (list):
        List of other condition objects

    """

    def __init__(self, conditions):

        self._conditions = conditions

    def tags(self):

        result = tuple()

        for _condition in self._conditions:
            result += _condition.tags()

        return tuple(set(result))

    def serialize(self):

        result = dict()
        result["type"] = "AndCondition"
        result["conditions"] = [_condition.serialize() for _condition in self._conditions]

        return result
    
    def evaluate(self):

        result = True

        for _condition in self._conditions:

            result = result and _condition.evaluate()

        return result


class Control:

    """Control class.

    This class defines a mechanism to apply controls
    on tags values, a control is defined by a condition and
    an action, once the condition is met, the action is 
    triggered

    # Example
    
    ```python
    >>> from rackio.controls import Action, Condition, Control
    >>> act1 = Action("T3", 40)
    >>> cond1 = Condition("T1",">=", "T2")
    >>> control1 = Control("C1", cond1, act1)
    ```

    # Parameters
    name (str):
        Condition name
    condition (Condition):
        Condition to inspect in this control
    action (Action):
        Action to be triggered once the condition is met
    
    """

    def __init__(self, name, condition, action):

        self._name = name
        self._condition = condition
        self._action = action

    @property
    def name(self):
        return self._name
        
    @property
    def condition(self):
        return self._condition    

    def serialize(self):

        result = dict()

        result["name"] = self._name
        result["condition"] = self._condition.serialize()
        result["action"] = self._action.serialize()

        return result

    def execute(self):

        if self._condition.evaluate():

            self._action.trigger()


class Rule:

    """Rule class.

    This class defines a mechanism to apply rules
    on tags values, a rule is defined by a condition and
    a list of actions, once the condition is met, the actions are 
    triggered in sequential order

    # Example
    
    ```python
    >>> from rackio.controls import Action, Condition, Rule
    >>> act1 = Action("T3", 40)
    >>> act2 = Action("T4", 60)
    >>> cond1 = Condition("T1",">=", "T2")
    >>> rule1 = Rule("C1", cond1, [act1, act2])
    ```

    # Parameters
    name (str):
        Condition name
    condition (Condition):
        Condition to inspect in this control
    action (Action):
        Action to be triggered once the condition is met
    
    """

    def __init__(self, name, condition, actions=None):

        self._name = name
        self._condition = condition

        if not actions:
            self._actions = list()
        else:
            self._actions = actions
    
    @property
    def name(self):
        return self._name

    @property
    def condition(self):
        return self._condition

    def serialize(self):

        result = dict()

        result["name"] = self._name
        result["condition"] = self._condition.serialize()
        result["actions"] = [action.serialize() for action in self._actions]

        return result
        
    def execute(self):

        if self._condition.evaluate():

            for _action in self._actions:
                _action.trigger()


class ControlManager:

    def __init__(self):

        self._rules = dict()
        self._controls = dict()
        self._tag_queue = queue.Queue()

    def rule_tags(self):
        
        result = list()
        
        for _tags in self._rules.keys():
            for _tag in _tags:
                result.append(_tag)

        return result

    def control_tags(self):
        
        result = list()
        
        for _tags in self._controls.keys():
            for _tag in _tags:
                result.append(_tag)

        return result
    
    def append_rule(self, rule):

        tags = rule._condition.tags()
        try:
            self._rules[tags].append(rule)
        except:
            self._rules[tags] = [rule]

    def append_control(self, control):

        tags = control._condition.tags()
        try:
            self._controls[tags].append(control)
        except:
            self._controls[tags] = [control]

    def get_rule(self, name):

        for _rules in self._rules.values():
            
            for _rule in _rules:
                
                if _rule.name == name:

                    return _rule

    def get_rules(self):

        result = list()

        for _rules in self._rules.values():

            result += _rules

        return result

    def get_control(self, name):

        for _controls in self._controls.values():
            
            for _control in _controls:

                if _control.name == name:  

                    return _control

    def get_controls(self):

        result = list()
        
        for _controls in self._controls.values():
            
            result += _controls

        return result

    def attach_all(self):

        _cvt = CVTEngine()

        def attach_observers(entities):

            for entity in entities:

                tags = entity.condition.tags()

                for _tag in tags:

                    observer = TagObserver(self._tag_queue)
                    query = dict()
                    query["action"] = "attach"
                    query["parameters"] = {
                        "name": _tag,
                        "observer": observer,
                    }

                    _cvt.request(query)
                    _cvt.response()

        for _tags, _control in self._controls.items():

            attach_observers(_control)

        for _tags, _rule in self._rules.items():

            attach_observers(_rule)

    def execute(self, tag):

        for _tags, _controls in self._controls.items():

            if tag in _tags:

                for _control in _controls:
                    _control.execute()

        for _tags, _rules in self._rules.items():

            if tag in _tags:

                for _rule in _rules:
                    _rule.execute()


class FunctionManager:

    def __init__(self):

        self._tags = dict()
        self._tag_queue = queue.Queue()

    def append_function(self, tag, function):

        try:
            self._tags[tag].append(function)
        except:
            self._tags[tag] = [function]

    def attach_all(self):

        _cvt = CVTEngine()

        for _tag in self._tags.keys():

            observer = TagObserver(self._tag_queue)
            query = dict()
            query["action"] = "attach"
            query["parameters"] = {
                "name": _tag,
                "observer": observer,
            }

            _cvt.request(query)
            _cvt.response()

    def execute(self, tag):

        try:
            for _function in self._tags[tag]:

                _function()
        except:
            pass

