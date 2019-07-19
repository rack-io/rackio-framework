# -*- coding: utf-8 -*-
"""rackio/workers.py

This module implements all thread classes for workers.
"""
import time
from threading import Thread
from wsgiref.simple_server import make_server

from .controls import ControlManager
from .engine import CVTEngine
from .dbmodels import TagTrend, TagValue, Event


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

    def __init__(self, manager, period=0.1):

        super(ControlWorker, self).__init__()
        
        self._manager = manager
        self._period = period

        self._manager.attach_all()

    def run(self):

        if (not self._manager.rule_tags()) and (not self._manager.control_tags()):
            return

        _queue = self._manager._tag_queue

        while True:
            
            time.sleep(self._period)

            if not _queue.empty():
                item = _queue.get()
                
                _tag = item["tag"]

                self._manager.execute(_tag)


class AlarmWorker(BaseWorker):

    def __init__(self, manager, period=0.25):

        super(AlarmWorker, self).__init__()
        
        self._manager = manager
        self._period = period

        self._manager.attach_all()

    def run(self):

        if not self._manager.alarms_tags():
            return

        _queue = self._manager._tag_queue

        while True:
            
            time.sleep(self._period)

            if not _queue.empty():
                item = _queue.get()
                
                _tag = item["tag"]

                self._manager.execute(_tag)


class _ContinousWorker:

    def __init__(self, f, worker_name=None, period=0.5, pause_tag=None, stop_tag=None):

        self._f = f
        self._name = worker_name
        self._period = period
        self._pause_tag = pause_tag
        self._stop_tag = stop_tag
        self._status = "Stop"       # ["Stop", "Pause", "Running", "Error"]

        from .core import Rackio

        rackio = Rackio()
        rackio._continous_functions.append(self)

    def serialize(self):

        result = dict()
        result["name"] = self._name
        result["period"] = self._period
        result["pause_tag"] = self._pause_tag
        result["stop_tag"] = self._stop_tag
        result["status"] = self._status

        return result

    def pause(self):

        if self._pause_tag:
            _cvt = CVTEngine()
            _cvt.write_tag(self._pause_tag, True)

            return True

    def resume(self):

        if self._pause_tag:
            _cvt = CVTEngine()
            _cvt.write_tag(self._pause_tag, False)

            return True

    def stop(self):

        if self._stop_tag:
            _cvt = CVTEngine()
            _cvt.write_tag(self._stop_tag, True)

            return True

    def get_name(self):

        return self._name

    def get_status(self):

        return self._status
    
    def __call__(self, *args):

        _cvt = CVTEngine()

        time.sleep(self._period)

        while True:

            self._status = "Running"

            now = time.time()

            if self._stop_tag:
                stop = _cvt.read_tag(self._stop_tag)

                if stop:
                    self._status = "Stop"
                    return

            if self._pause_tag:
                pause = _cvt.read_tag(self._pause_tag)
                
                if not pause:
                    
                    try:
                        self._f()
                    except:
                        self._status = "Error"
                else:
                    self._status = "Pause"

            else:
                try:
                    self._f()
                except:
                    self._status = "Error"

            elapsed = time.time() - now

            if elapsed < self._period:
                time.sleep(self._period - elapsed)
            

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


class LoggerWorker(BaseWorker):

    def __init__(self, manager):

        super(LoggerWorker, self).__init__()
        
        self._manager = manager
        self._period = manager.get_period()

    def run(self):

        self._manager._logger._db.create_tables([TagTrend, TagValue, Event])

        for tag in self._manager._logging_tags:

            self._manager._logger.set_tag(tag)

        _cvt = CVTEngine()

        time.sleep(self._period)

        while True:

            now = time.time()

            for _tag in self._manager._logging_tags:
                value = _cvt.read_tag(_tag)
                self._manager.write_tag(_tag, value)
            
            elapsed = time.time() - now

            if elapsed < self._period:
                time.sleep(self._period - elapsed)
            else:
                print("Failed to log on item...")
            