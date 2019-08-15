# -*- coding: utf-8 -*-
"""rackio/api/api.py

This module implements all class Resources for the RESTful API.
"""

import json
import falcon

from datetime import datetime

from rackio import status_code

from ..engine import CVTEngine
from ..logger import QueryLogger, LoggerEngine
from ..events import Event


class RackioResource(object):

    from ..core import Rackio

    tag_engine = CVTEngine()
    logger_engine = LoggerEngine()
    query_logger = QueryLogger()
    
    def get_app(self):

        from ..core import Rackio

        return Rackio()


class ControlCollectionResource(object):

    def on_get(self, req, resp):
        
        from ..core import Rackio

        app = Rackio()
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


class ControlResource(object):

    def on_get(self, req, resp, control_name):
        
        from ..core import Rackio

        app = Rackio()
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


class RuleCollectionResource(object):

    def on_get(self, req, resp):
        
        from ..core import Rackio

        app = Rackio()
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


class RuleResource(object):

    def on_get(self, req, resp, rule_name):
        
        from ..core import Rackio

        app = Rackio()
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


class ContinousWorkerResource(object):

    def on_get(self, req, resp, worker_name):
        
        from ..core import Rackio

        app = Rackio()
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
        
        from ..core import Rackio
        
        action = req.media.get('action')

        app = Rackio()
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


class EventCollectionResource(RackioResource):

    def on_get(self, req, resp):

        _logger = LoggerEngine()

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
        
        _logger = LoggerEngine()
        
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