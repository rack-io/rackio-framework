# -*- coding: utf-8 -*-
"""rackio/api/log_hook.py

This module implements a hook class caller for decorating RackioResources.
"""
import logging
from .hook import rackio_hook
from datetime import datetime
from rackio.events import Event
from rackio.logger import LoggerEngine


class Log(object):

    def __call__(self, request, response, resource, params):

        username = request.media.get('username')

        logging.info("{}: made {} request".format(username, resource.__class__.__name__))


log = rackio_hook.before(Log())


class NotifyAlarmOperation(object):

    def __init__(self):

        self._logger = LoggerEngine()

    def get_app(self):

        from ..core import Rackio

        return Rackio()

    def __call__(self, request, response, resource, params):

        username = request.media.get('username')
        action = request.media.get('action')

        if 'alarm_name' in params:

            alarm_name = params['alarm_name']
            event_values = dict(user='{}'.format(username),
                                message='Alarm operation: {}'.format(action),
                                description='Operation {} in {}'.format(action, alarm_name),
                                classification='{}'.format('user'),
                                priority='{}'.format(3),
                                date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        else:

            event_values = dict(user='{}'.format(username),
                            message='Alarm operation: {}'.format(action),
                            description='Operation: {}'.format(action),
                            classification='{}'.format('user'),
                            priority='{}'.format(3),
                            date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        event = Event(**event_values)
        self._logger.write_event(event)


notify_alarm_operation = rackio_hook.before(NotifyAlarmOperation())


class NotifyRestartSystems(object):

    def __init__(self):

        self._logger = LoggerEngine()

    def get_app(self):

        from ..core import Rackio

        return Rackio()

    def __call__(self, request, response, resource, params):

        app = self.get_app()

        username = request.media.get('username')
        machines = app.get_machines()

        for machine, _, _ in machines:
            
            if hasattr(machine, 'restart'):

                event_values = {
                    'user': '{}'.format(username),
                    'message': '{} {}'.format(machine.name, "restarting"),
                    'description': '{} machine was switched to {}'.format(machine.name, "restarting"),
                    'classification': '{}'.format(machine.classification),
                    'priority': '{}'.format(machine.priority),
                    'date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                event = Event(**event_values)
                self._logger.write_event(event)


notify_restart_systems = rackio_hook.before(NotifyRestartSystems())
