# -*- coding: utf-8 -*-
"""rackio/api/alarms.py

This module implements all class Resources for the Alarm Manager.
"""

import json

from rackio import status_code

from .api import RackioResource


class AlarmCollectionResource(RackioResource):

    def on_get(self, req, resp):

        app = self.get_app()
        manager = app._alarm_manager

        doc = list()

        for alarm in manager.get_alarms():

            doc.append(alarm.serialize())
            
        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        # resp.status = falcon.HTTP_200
        resp.status = status_code.HTTP_200
 

class AlarmResource(RackioResource):

    def on_get(self, req, resp, alarm_name):

        app = self.get_app()
        manager = app._alarm_manager

        alarm = manager.get_alarm(alarm_name)

        if alarm:
            doc = alarm.serialize()
            
            # Create a JSON representation of the resource
            resp.body = json.dumps(doc, ensure_ascii=False)

            # The following line can be omitted because 200 is the default
            # status returned by the framework, but it is included here to
            # illustrate how this may be overridden as needed.
            # resp.status = falcon.HTTP_200
            resp.status = status_code.HTTP_200
        else:
            resp.status = status_code.HTTP_NOT_FOUND

    def on_post(self, req, resp, alarm_name):
        
        from ..core import Rackio
        
        action = req.media.get('action')

        app = Rackio()
        manager = app._alarm_manager

        alarm = manager.get_alarm(alarm_name)

        if alarm:
            if action == "Acknowledge":

                alarm.acknowledge()
            
            elif action == "Enable":

                alarm.enable()

            elif action == "Disable":

                alarm.disable()

            doc = alarm.serialize()

            # Create a JSON representation of the resource
            resp.body = json.dumps(doc, ensure_ascii=False)

            # The following line can be omitted because 200 is the default
            # status returned by the framework, but it is included here to
            # illustrate how this may be overridden as needed.
            # resp.status = falcon.HTTP_200
            resp.status = status_code.HTTP_200
        else:
            resp.status = status_code.HTTP_NOT_FOUND
            