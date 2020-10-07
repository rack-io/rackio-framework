# -*- coding: utf-8 -*-
"""rackio/api/controls.py

This module implements all class Resources for the Controls and Rules.
"""

import json

from rackio import status_code

from .core import RackioResource
from ..dao import ControlsDAO, RulesDAO


class ControlBaseResource(RackioResource):
    
    dao = ControlsDAO()


class ControlCollectionResource(ControlBaseResource):

    def on_get(self, req, resp):

        doc = self.dao.get_all()

        resp.body = json.dumps(doc, ensure_ascii=False)


class ControlResource(ControlBaseResource):

    def on_get(self, req, resp, control_name):

        doc = self.dao.get(control_name)

        if doc:
            resp.body = json.dumps(doc, ensure_ascii=False)
        else:
            resp.status = status_code.HTTP_NOT_FOUND


class RuleBaseResource(RackioResource):
    
    dao = RulesDAO()


class RuleCollectionResource(RuleBaseResource):

    def on_get(self, req, resp):

        doc = self.dao.get_all()
            
        resp.body = json.dumps(doc, ensure_ascii=False)


class RuleResource(RuleBaseResource):

    def on_get(self, req, resp, rule_name):
        
        doc = self.dao.get(rule_name)

        if doc:
            resp.body = json.dumps(doc, ensure_ascii=False)
        else:
            resp.status = status_code.HTTP_NOT_FOUND
            