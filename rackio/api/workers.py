# -*- coding: utf-8 -*-
"""rackio/api/workers.py

This module implements all class Resources for Rackio Workers.
"""

import json

from rackio import status_code

from .core import RackioResource


class ContinousWorkerResource(RackioResource):

    def on_get(self, req, resp, worker_name):

        app = self.get_app()
        manager = app._alarm_manager

        alarm = manager.get_alarm(worker_name)

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
        
        action = req.media.get('action')

        app = self.get_app()
        manager = app._alarm_manager

        alarm = manager.get_alarm(alarm_name)

        if alarm:
            if action == "Acknowledge":

                alarm.acknowledge()

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
