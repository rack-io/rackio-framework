# -*- coding: utf-8 -*-
"""rackio/api/alarms.py

This module implements all class Resources for the Alarm Manager.
"""

import json

from rackio import status_code

from .core import RackioResource
from ..dao import AlarmsDAO


class BaseResource(RackioResource):
    
    dao = AlarmsDAO()


class AlarmCollectionResource(BaseResource):

    def on_get(self, req, resp):

        doc = self.dao.get_all()
        
        resp.body = json.dumps(doc, ensure_ascii=False)
 

class AlarmResource(BaseResource):

    def on_get(self, req, resp, alarm_name):

        doc = self.dao.get(alarm_name)

        if doc:
            
            resp.body = json.dumps(doc, ensure_ascii=False)

        else:
            resp.status = status_code.HTTP_NOT_FOUND

    def on_post(self, req, resp, alarm_name):
        
        action = req.media.get('action')

        doc = self.dao.update(alarm_name, action)

        resp.body = json.dumps(doc, ensure_ascii=False)
            
            