# -*- coding: utf-8 -*-
"""rackio/dao/events.py

This module implements Events Data Objects Access.
"""
from .core import RackioDAO

from ..events import Event
from ..utils import serialize_dbo


class EventsDAO(RackioDAO):
    def get_all(self):
        _logger = self.logger_engine

        events = _logger.read_events()

        try:
            result = {
                "events": [serialize_dbo(event) for event in events],
            }
        except:
            result = {"events": events}

        return result

    def write(self, user, message, description, priority, criticity):
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        event = Event(
            user=user,
            message=message,
            description=description,
            priority=priority,
            criticity=criticity,
            date_time=date_time,
        )

        try:
            _logger.write_event(event)

            result = {"result": True}
        except:
            result = {"result": False}

        return result
