# -*- coding: utf-8 -*-
"""rackio/workers/controls.py

This module implements Control Worker.
"""
import time

from .worker import BaseWorker


class ControlWorker(BaseWorker):

    def __init__(self, manager, period=0.1):

        super(ControlWorker, self).__init__()
        
        self._manager = manager
        self._period = period

        self._manager.attach_all()

    def run(self):

        if (not self._manager.rule_tags()) and (not self._manager.control_tags()):
            return

        self._manager.execute_all()

        _queue = self._manager.get_queue()

        while True:

            if not _queue.empty():
                item = _queue.get()
                
                _tag = item["tag"]

                self._manager.execute(_tag)
            else:
                time.sleep(self._period)
