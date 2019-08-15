# -*- coding: utf-8 -*-
"""rackio/api/controls.py

This module implements all class Resources for the Controls and Rules.
"""

import json

from rackio import status_code

from .api import RackioResource


class ControlCollectionResource(RackioResource):

    def on_get(self, req, resp):

        app = self.get_app()
        manager = app._control_manager

        doc = list()

        for control in manager.get_controls():

            doc.append(control.serialize())
            
        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        # resp.status = falcon.HTTP_200
        resp.status = status_code.HTTP_200


class ControlResource(RackioResource):

    def on_get(self, req, resp, control_name):

        app = self.get_app()
        manager = app._control_manager

        control = manager.get_control(control_name)

        if control:
            doc = control.serialize()
            
            # Create a JSON representation of the resource
            resp.body = json.dumps(doc, ensure_ascii=False)

            # The following line can be omitted because 200 is the default
            # status returned by the framework, but it is included here to
            # illustrate how this may be overridden as needed.
            # resp.status = falcon.HTTP_200
            resp.status = status_code.HTTP_200
        else:
            resp.status = status_code.HTTP_NOT_FOUND


class RuleCollectionResource(RackioResource):

    def on_get(self, req, resp):

        app = self.get_app()
        manager = app._control_manager

        doc = list()

        for rule in manager._rules:

            doc.append(rule.serialize())
            
        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        # resp.status = falcon.HTTP_200
        resp.status = status_code.HTTP_200


class RuleResource(RackioResource):

    def on_get(self, req, resp, rule_name):
        
        app = self.get_app()
        manager = app._control_manager

        rule = manager.get_rule(rule_name)

        if rule:
            doc = rule.serialize()
            
            # Create a JSON representation of the resource
            resp.body = json.dumps(doc, ensure_ascii=False)

            # The following line can be omitted because 200 is the default
            # status returned by the framework, but it is included here to
            # illustrate how this may be overridden as needed.
            # resp.status = falcon.HTTP_200
            resp.status = status_code.HTTP_200
        else:
            resp.status = status_code.HTTP_NOT_FOUND
            