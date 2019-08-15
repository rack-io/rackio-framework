# -*- coding: utf-8 -*-
"""rackio/api/events.py

This module implements all class Resources for Events.
"""

import json
from datetime import datetime

from rackio import status_code

from .core import RackioResource

from ..events import Event


class EventCollectionResource(RackioResource):

    def on_get(self, req, resp):

        _logger = self.logger_engine

        events = _logger.read_events()

        try:
            doc = {
                'events': [serialize_dbo(event) for event in events],
            }
        except:
            doc = {
                'events': events
            }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        # resp.status = falcon.HTTP_200
        resp.status = status_code.HTTP_200

    def on_post(self, req, resp):
        
        _logger = self.logger_engine
        
        user = req.media.get('user')
        message = req.media.get('message')
        description = req.media.get('description')
        priority = req.media.get('priority')
        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        event  = Event(user=user, message=message, description=description, priority=priority, date_time=date_time)

        try:
            _logger.write_event(event)

            doc = {
                'result': True
            }
        except:
            doc = {
                'result': False
            }


        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)
        resp.status = status_code.HTTP_200