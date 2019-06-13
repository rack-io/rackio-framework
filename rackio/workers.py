# -*- coding: utf-8 -*-
"""rackio/workers.py

This module implements all thread classes for workers.
"""
import time
from threading import Thread
from wsgiref.simple_server import make_server

from .controls import ControlManager
from .engine import CVTEngine

class BaseWorker(Thread):

    def  __init__(self):

        super(BaseWorker, self).__init__()


class ThreadWorker(BaseWorker):

    def  __init__(self, worker_function, period):

        super(ThreadWorker, self).__init__()
        self._period = period
        self._worker_function = worker_function

    def run(self):

        while True:

            time.sleep(self._period)

            self._worker_function()


class ControlWorker(BaseWorker):

    def __init__(self, manager):

        super(ControlWorker, self).__init__()
        
        self._manager = manager
        self._manager.attach_all()

    def run(self):

        _queue = self._manager._tag_queue

        while True:
            
            time.sleep(0.1)

            if not _queue.empty():
                item = _queue.get()
                
                _tag = item["tag"]

                self._manager.execute(_tag)


class AlarmWorker(BaseWorker):

    def __init__(self, manager):

        super(AlarmWorker, self).__init__()
        
        self._manager = manager
        self._manager.attach_all()

    def run(self):

        _queue = self._manager._tag_queue

        while True:
            
            time.sleep(0.1)

            if not _queue.empty():
                item = _queue.get()
                
                _tag = item["tag"]

                self._manager.execute(_tag)


class _ContinousWorker:

    def __init__(self, f, period=0.5, pause_tag=None, stop_tag=None):

        self._f = f
        self._period = period
        self._pause_tag = pause_tag
        self._stop_tag = stop_tag

        from .core import Rackio

        rackio = Rackio()
        rackio._continous_functions.append(self)
    
    def __call__(self, *args):

        _cvt = CVTEngine()
        while True:

            time.sleep(self._period)

            if self._pause_tag:
                stop = _cvt.read_tag(self._stop_tag)

                if stop:
                    return

            if self._pause_tag:
                pause = _cvt.read_tag(self._pause_tag)

                if not pause:
                    
                    self._f()
            else:
                self._f()

class APIWorker(BaseWorker):

    def __init__(self, app, port=8000):

        super(APIWorker, self).__init__()

        self._api_app = app
        self._port = port

    def run(self):

        with make_server('', self._port, self._api_app) as httpd:
            print('Serving on port {}...'.format(self._port))

            # Serve until process is killed
            httpd.serve_forever()