# -*- coding: utf-8 -*-
"""rackio/workers/functions.py

This module implements Function Worker.
"""
import time

from .worker import BaseWorker


class FunctionWorker(BaseWorker):

    def __init__(self, manager, period=0.1):

        super(FunctionWorker, self).__init__()
        
        self._manager = manager
        self._period = period

        self._manager.attach_all()

    def run(self):

        if not self._manager._tags:
            return
        
        _queue = self._manager.get_queue()

        while True:

            if not _queue.empty():
                item = _queue.get()
                
                _tag = item["tag"]

                self._manager.execute(_tag)
            else:
                time.sleep(self._period)

            if self.stop_event.is_set():
                break
    