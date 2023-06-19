# -*- coding: utf-8 -*-
"""rackio/managers/controls.py

This module implements Control Manager.
"""
import queue

from ..engine import CVTEngine
from ..models import TagObserver


class ControlManager:
    def __init__(self):
        self._rules = dict()
        self._controls = dict()
        self._tag_queue = queue.Queue()

    def get_queue(self):
        return self._tag_queue

    def rule_tags(self):
        result = list()

        for _tags in self._rules:
            for _tag in _tags:
                result.append(_tag)

        return result

    def control_tags(self):
        result = list()

        for _tags in self._controls:
            for _tag in _tags:
                result.append(_tag)

        return result

    def append_rule(self, rule):
        tags = rule.condition.tags()
        try:
            self._rules[tags].append(rule)
        except Exception as e:
            self._rules[tags] = [rule]

    def append_control(self, control):
        tags = control.condition.tags()
        try:
            self._controls[tags].append(control)
        except Exception as e:
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

    def summary(self):
        result = dict()

        controls = self.get_controls()

        result["controls"] = {
            "length": len(controls),
            "items": [control.name for control in controls],
        }

        rules = self.get_rules()

        result["rules"] = {"length": len(rules), "items": [rule.name for rule in rules]}

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

    def execute_all(self):
        for _tags, _controls in self._controls.items():
            for _control in _controls:
                _control.execute()

        for _tags, _rules in self._rules.items():
            for _rule in _rules:
                _rule.execute()
