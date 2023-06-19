# -*- coding: utf-8 -*-
"""rackio/workers/alarms.py

This module implements Alarm Worker.
"""
import logging
import time

from .worker import BaseWorker


class AlarmWorker(BaseWorker):
    def __init__(self, manager, period=0.1):
        super(AlarmWorker, self).__init__()

        self._manager = manager
        self._period = period

        self._manager.attach_all()

    def run(self):
        if not self._manager.alarm_tags():
            return

        _queue = self._manager.get_queue()

        while True:
            time.sleep(self._period)

            if not _queue.empty():
                item = _queue.get()

                _tag = item["tag"]

                self._manager.execute(_tag)

            if self.stop_event.is_set():
                break

        logging.info("Alarm worker shutdown successfully!")
