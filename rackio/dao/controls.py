# -*- coding: utf-8 -*-
"""rackio/dao/controls.py

This module implements Controls Data Objects Access.
"""
from .core import RackioDAO


class ControlsDAO(RackioDAO):

    def get_all(self):
    
        app = self.get_app()
        manager = app.get_manager("control")

        result = list()

        for control in manager.get_controls():

            result.append(control.serialize())

        return result

    def get(self, name):

        app = self.get_app()
        manager = app.get_manager("control")

        control = manager.get_control(name)

        if control:
            return control.serialize()


class RulesDAO(RackioDAO):
    
    def get_all(self):
    
        app = self.get_app()
        manager = app.get_manager("control")

        result = list()

        for rule in manager.get_rules():

            result.append(rule.serialize())

        return result

    def get(self, name):

        app = self.get_app()
        manager = app.get_manager("control")

        rule = manager.get_rule(name)

        if rule:
            return rule.serialize()
