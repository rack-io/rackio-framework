# -*- coding: utf-8 -*-
"""rackio/api/alarms.py

This module implements all class Resources for the Alarm Manager.
"""

import json

from rackio import status_code

from .core import RackioResource


class AlarmCollectionResource(RackioResource):

    def on_get(self, req, resp):

        app = self.get_app()
        manager = app._alarm_manager

        doc = list()

        for alarm in manager.get_alarms():

            doc.append(alarm.serialize())
        
        resp.body = json.dumps(doc, ensure_ascii=False)
 

class AlarmResource(RackioResource):

    def on_get(self, req, resp, alarm_name):

        app = self.get_app()
        manager = app._alarm_manager

        alarm = manager.get_alarm(alarm_name)

        if alarm:
            doc = alarm.serialize()
            
            resp.body = json.dumps(doc, ensure_ascii=False)

        else:
            resp.status = status_code.HTTP_NOT_FOUND

    def on_post(self, req, resp, alarm_name):
        
        action = req.media.get('action')

        app = self.get_app()
        manager = app._alarm_manager

        alarm = manager.get_alarm(alarm_name)

        if alarm:
            if action == "Acknowledge":

                alarm.acknowledge()
            
            elif action == "Enable":

                alarm.enable()

            elif action == "Disable":

                alarm.disable()

            elif action == "Reset":

                alarm.reset()

            doc = alarm.serialize()

            resp.body = json.dumps(doc, ensure_ascii=False)

        else:
            resp.status = status_code.HTTP_NOT_FOUND
            