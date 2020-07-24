# -*- coding: utf-8 -*-
"""rackio/workers.py

This module implements all thread classes for workers.
"""
import time
import logging

from threading import Thread
from threading import Event as ThreadEvent
from wsgiref.simple_server import make_server

from apscheduler.schedulers.background import BackgroundScheduler

from .engine import CVTEngine
from .dbmodels import TagTrend, TagValue, Event
from .handlers import CustomWSGIRequestHandler


class BaseWorker(Thread):

    def  __init__(self):

        super(BaseWorker, self).__init__()

        self.stop_event = ThreadEvent()
        self.tag_engine = CVTEngine()

    def get_stop_event(self):

        return self.stop_event


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

        self._manager.execute_all()

        _queue = self._manager.get_queue()

        while True:

            if not _queue.empty():
                item = _queue.get()
                
                _tag = item["tag"]

                self._manager.execute(_tag)
            else:
                time.sleep(self._period)


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


class AlarmWorker(BaseWorker):

    def __init__(self, manager, period=0.25):

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


class StateMachineWorker():

    def __init__(self, manager):
        
        self._manager = manager
        self._scheduler = BackgroundScheduler()
        logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)

        self.jobs = list()

    def loop_closure(self, machine):

        def loop():

            machine.loop()

        return loop

    def start(self):

        for machine, interval in self._manager.get_machines():
            
            loop = self.loop_closure(machine)
            job = self._scheduler.add_job(loop, 'interval', seconds=interval)

            self.jobs.append(job)
        
        self._scheduler.start()


STOP = "Stop"
PAUSE = "Pause"
RUNNING = "Running"
ERROR = "Error"


class _ContinousWorker:

    def __init__(self, f, worker_name=None, period=0.5, error_message=None, pause_tag=None, stop_tag=None):

        self._f = f

        if not worker_name:
            worker_name = f.__name__

        self._name = worker_name
        self._period = period

        self._error_message = error_message
        self._pause_tag = pause_tag
        self._stop_tag = stop_tag
        self._status = STOP       # [STOP, PAUSE, RUNNING, ERROR]

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

            self._status = RUNNING

            now = time.time()

            if self._stop_tag:
                stop = _cvt.read_tag(self._stop_tag)

                if stop:
                    self._status = STOP
                    return

            if self._pause_tag:
                pause = _cvt.read_tag(self._pause_tag)
                
                if not pause:
                    
                    try:
                        self._f()
                    except Exception as e:
                        error = str(e)
                        
                        if not self._error_message:
                            logging.error("Worker - {}:{}".format(self._name, error))
                        else:
                            logging.error("Worker - {}:{}:{}".format(self._name, self._error_message, error))
                        
                        self._status = ERROR

                else:
                    self._status = PAUSE

            else:
                try:
                    self._f()
                except Exception as e:
                    error = str(e)

                    if not self._error_message:
                        logging.error("Worker - {}:{}".format(self._name, error))
                    else:
                        logging.error("Worker - {}:{}:{}".format(self._name, self._error_message, error))
                    self._status = ERROR

            elapsed = time.time() - now

            if elapsed < self._period:
                time.sleep(self._period - elapsed)
            else:
                logging.warning("Worker - {}: Unable to perform on time...".format(self._name))
            

class APIWorker(BaseWorker):

    def __init__(self, app, port=8000):

        super(APIWorker, self).__init__()

        self._api_app = app
        self._port = port

    def run(self):

        with make_server('', self._port, self._api_app, handler_class=CustomWSGIRequestHandler) as httpd:
            logging.info('Serving on port {}...'.format(self._port))
            httpd.serve_forever()


class LoggerWorker(BaseWorker):

    def __init__(self, manager):

        super(LoggerWorker, self).__init__()
        
        self._manager = manager
        self._period = manager.get_period()
        self._delay = manager.get_delay()

        self.last = None

    def set_last(self):

        self.last = time.time()

    def sleep_elapsed(self):

        elapsed = time.time() - self.last

        if elapsed < self._period:
            time.sleep(self._period - elapsed)
        else:
            logging.warning("Logger Worker: Failed to log items on time...")

        self.set_last()

    def verify_workload(self):

        tags = self._manager.get_tags()

        if not tags:
            return False

        db = self._manager.get_db()

        if not db:
            return False

        return True

    def init_database(self):

        if self._manager.get_dropped():
            try:
                self._manager.drop_tables([TagTrend, TagValue, Event])
            except Exception as e:
                error = str(e)
                logging.error("Database:{}".format(error))

        self._manager.create_tables([TagTrend, TagValue, Event])

    def set_tags(self):

        tags = self._manager.get_tags()
        
        for tag in tags:

            self._manager.set_tag(tag)

    def write_tags(self):

        for _tag in self._manager.get_tags():
            value = self.tag_engine.read_tag(_tag)
            self._manager.write_tag(_tag, value)

    def run(self):

        if not self.verify_workload():
            return

        self.init_database()
        self.set_tags()
        
        time.sleep(self._delay)
        time.sleep(self._period)

        self.set_last()

        while True:

            self.write_tags()
            self.sleep_elapsed()

           
            