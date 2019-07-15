# -*- coding: utf-8 -*-
"""rackio/models.py

This module implements all class Resources for the RESTful API.
"""

import json
import falcon

from datetime import datetime

from rackio import status_code

from .engine import CVTEngine
from .logger import QueryLogger, LoggerEngine
from .utils import process_waveform
from .events import Event


class RackioResource(object):

    def __init__(self):

        self.tag_engine = CVTEngine()


class TagCollectionResource(object):

    def on_get(self, req, resp):

        doc = list()

        _cvt = CVTEngine()
        tags = _cvt.get_tags()

        for _tag in tags:

            value = _cvt.read_tag(_tag)
            
            try:
                result = {
                    'tag': _tag,
                    'value': value._serialize()
                }
            except:
                result = {
                    'tag': _tag,
                    'value': value
                }

            doc.append(result)

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        # resp.status = falcon.HTTP_200
        resp.status = status_code.HTTP_200


class TagResource(RackioResource):

    def on_get(self, req, resp, tag_id):

        # _cvt = CVTEngine()
        _cvt = self.tag_engine

        value = _cvt.read_tag(tag_id)

        try:
            doc = {
                'tag': tag_id,
                'value': value._serialize()
            }
        except:
            doc = {
                'tag': tag_id,
                'value': value
            }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        # resp.status = falcon.HTTP_200
        resp.status = status_code.HTTP_200

    def on_post(self, req, resp, tag_id):
        
        value = req.media.get('value')

        _cvt = CVTEngine()
        _type = _cvt.read_type(tag_id)

        if _type == "float":
            value = float(value)
        elif _type == "int":
            value = int(value)
        elif _type == "bool":
            if value == "true":
                value = True
            elif value == "false":
                value = False
            else:
                value = bool(value)

        _cvt.write_tag(tag_id, value)

        doc = {
            'result': True
        }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)
        resp.status = status_code.HTTP_200


class TagHistoryResource(object):

    def on_get(self, req, resp, tag_id):

        _logger = LoggerEngine()

        history = _logger.read_tag(tag_id)

        waveform = dict() 
        waveform["dt"] = history["dt"]
        waveform["t0"] = history["t0"]
        # waveform["t0"] = history["t0"].strftime('%Y-%m-%d %H:%M:%S')
        waveform["values"] = history["values"]

        doc = {
            'tag': tag_id,
            'waveform': waveform
        }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        # resp.status = falcon.HTTP_200
        resp.status = status_code.HTTP_200

    
class TrendResource(object):

    def on_post(self, req, resp, tag_id):

        tstart = req.media.get('tstart')
        tstop = req.media.get('tstop')

        _query_logger = QueryLogger()
        result = _query_logger.query(tag_id, tstart, tstop)

        doc = {
            'tag': tag_id,
            'waveform': result
        }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        # resp.status = falcon.HTTP_200
        resp.status = status_code.HTTP_200


class AlarmCollectionResource(object):

    def on_get(self, req, resp):
        
        from .core import Rackio

        app = Rackio()
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
 

class AlarmResource(object):

    def on_get(self, req, resp, alarm_name):
        
        from .core import Rackio

        app = Rackio()
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
        
        from .core import Rackio
        
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


class ContinousWorkerResource(object):

    def on_get(self, req, resp, worker_name):
        
        from .core import Rackio

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
        
        from .core import Rackio
        
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
                'events': [event._serialize() for event in events],
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

        event = {
            "user": user,
            "message": message,
            "description": description,
            "priority": priority,
            "datetime": date_time
        }

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