# -*- coding: utf-8 -*-
"""rackio/workers/worker.py

This module implements all thread classes for workers.
"""
from threading import Thread
from threading import Event as ThreadEvent

from ..engine import CVTEngine


class BaseWorker(Thread):

    def  __init__(self):

        super(BaseWorker, self).__init__()

        self.stop_event = ThreadEvent()
        self.tag_engine = CVTEngine()

    def get_stop_event(self):

        return self.stop_event

    def stop(self):

        self.stop_event.set()
    