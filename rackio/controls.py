# -*- coding: utf-8 -*-
"""rackio/models.py

This module implements a Controls classes for taking
actions into Tags oberservers.
"""
import queue

from pybigparser.evaluator import get_vars, MathParser

from .engine import CVTEngine
from .models import TagObserver

GT = ">"
LT = "<"
GTE = ">="
LTE = "<="
EQ = "=="
NEQ = "!="


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
    tag values

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
    on tag values

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
        
        value1 = _cvt.read_tag(self.tag1)
        value2 = _cvt.read_tag(self.tag2)

        result = False

        if _oper == EQ:

            result = value1 == value2

        elif _oper == NEQ:

            result = value1 != value2
        
        elif _oper == LT:

            result = value1 < value2

        elif _oper == LTE:

            result = value1 <= value2

        elif _oper == GT:

            result = value1 > value2

        elif _oper == GTE:

            result = value1 >= value2

        else:
            result = False

        return result


class BoolCondition:

    """BooleanCondition class.

    This class defines a mechanism to apply conditions
    on boolean tag values

    # Example
    
    ```python
    >>> from rackio.controls import BoolCondition
    >>> cond1 = BoolCondition("HIGH_ALARM")
    ```

    # Parameters
    tag (str):
        tag name
    """

    def __init__(self, tag):

        self.tag = tag
        self._cvt = CVTEngine()

    def evaluate(self):

        result = self._cvt.read_tag(self.tag)

        if result:
            return True

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

        conditions = self._conditions
        result = dict()
        result["type"] = "OrCondition"
        result["conditions"] = [_cond.serialize() for _cond in conditions]

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

        conditions = self._conditions
        result = dict()
        result["type"] = "AndCondition"
        result["conditions"] = [_cond.serialize() for _cond in conditions]

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
