# -*- coding: utf-8 -*-
"""rackio/api/controls.py

This module implements all class Resources for the Controls and Rules.
"""

import json

from rackio import status_code

from .core import RackioResource


class ControlCollectionResource(RackioResource):

    def on_get(self, req, resp):

        app = self.get_app()
        manager = app.get_manager("control")

        doc = list()

        for control in manager.get_controls():

            doc.append(control.serialize())

        resp.body = json.dumps(doc, ensure_ascii=False)


class ControlResource(RackioResource):

    def on_get(self, req, resp, control_name):

        app = self.get_app()
        manager = app.get_manager("control")

        control = manager.get_control(control_name)

        if control:
            doc = control.serialize()

            resp.body = json.dumps(doc, ensure_ascii=False)

        else:
            resp.status = status_code.HTTP_NOT_FOUND


class RuleCollectionResource(RackioResource):

    def on_get(self, req, resp):

        app = self.get_app()
        manager = app.get_manager("control")

        doc = list()

        for rule in manager.get_rules():

            doc.append(rule.serialize())
            
        resp.body = json.dumps(doc, ensure_ascii=False)


class RuleResource(RackioResource):

    def on_get(self, req, resp, rule_name):
        
        app = self.get_app()
        manager = app.get_manager("control")

        rule = manager.get_rule(rule_name)

        if rule:
            doc = rule.serialize()

            resp.body = json.dumps(doc, ensure_ascii=False)
            
        else:
            resp.status = status_code.HTTP_NOT_FOUND
            