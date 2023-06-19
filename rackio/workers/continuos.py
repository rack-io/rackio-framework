# -*- coding: utf-8 -*-
"""rackio/workers/continuos.py

This module implements Continuos Worker.
"""
import time
import logging

from ..engine import CVTEngine

STOP = "Stop"
PAUSE = "Pause"
RUNNING = "Running"
ERROR = "Error"


class _ContinuosWorker:
    def __init__(
        self,
        f,
        worker_name=None,
        period=0.5,
        error_message=None,
        pause_tag=None,
        stop_tag=None,
    ):
        self._f = f

        if not worker_name:
            worker_name = f.__name__

        self._name = worker_name
        self._period = period

        self._error_message = error_message
        self._pause_tag = pause_tag
        self._stop_tag = stop_tag
        self._status = STOP  # [STOP, PAUSE, RUNNING, ERROR]

        self.tag_engine = CVTEngine()

        self.last = None

        from ..core import Rackio

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

    def set_last(self):
        self.last = time.time()

    def sleep_elapsed(self):
        elapsed = time.time() - self.last

        if elapsed < self._period:
            time.sleep(self._period - elapsed)
        else:
            logging.warning("Logger Worker: Failed to log items on time...")

        self.set_last()

    def pause(self):
        if self._pause_tag:
            self.tag_engine.write_tag(self._pause_tag, True)

            return True

    def resume(self):
        if self._pause_tag:
            self.tag_engine.write_tag(self._pause_tag, False)

            return True

    def stop(self):
        if self._stop_tag:
            self.tag_engine.write_tag(self._stop_tag, True)

            return True

    def get_name(self):
        return self._name

    def get_status(self):
        return self._status

    def log_error(self, e):
        error = str(e)

        if self._error_message:
            logging.error(
                "Worker - {}:{}:{}".format(self._name, self._error_message, error)
            )
        else:
            logging.error("Worker - {}:{}".format(self._name, error))

    def is_paused(self):
        pause = False

        if self._pause_tag:
            pause = self.tag_engine.read_tag(self._pause_tag)

        return pause

    def is_stopped(self):
        stop = False

        if self._stop_tag:
            stop = self.tag_engine.read_tag(self._stop_tag)

        return stop

    def __call__(self, *args):
        time.sleep(self._period)

        self.set_last()

        self._status = RUNNING

        while True:
            if self.is_stopped():
                self._status = STOP
                return

            if self.is_paused():
                self._status = PAUSE
                continue
            else:
                self._status = RUNNING
                try:
                    self._f()
                except Exception as e:
                    self.log_error(e)
                    self._status = ERROR

            self.sleep_elapsed()
