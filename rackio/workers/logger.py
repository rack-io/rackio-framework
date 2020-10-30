# -*- coding: utf-8 -*-
"""rackio/workers/logger.py

This module implements Logger Worker.
"""
import time
import logging

from .worker import BaseWorker
from ..logger import LoggerEngine
from ..utils import chunks, log_detailed


class MicroLoggerWorker(BaseWorker):

    def __init__(self, tags, period):

        super(MicroLoggerWorker, self).__init__()

        self.tags = tags
        self._period = period
        self.last = None
        self.compensation = 0.0

        self._logger = LoggerEngine()

    def set_last(self):

        self.last = time.time()

    def sleep_elapsed(self):

        elapsed = time.time() - self.last

        if elapsed < self._period:
            time.sleep(self._period - elapsed)
        else:
            logging.warning("Logger Worker: Failed to log items on time...")

        self.set_last()

    def write_tags(self):

        for _tag in self.tags:
            value = self.tag_engine.read_tag(_tag)
            self._logger.write_tag(_tag, value)

    def run(self):

        time.sleep(self._period)

        self.set_last()

        while True:

            self.write_tags()
            self.sleep_elapsed()

            if self.stop_event.is_set():
                break


class LoggerWorker(BaseWorker):

    def __init__(self, manager):

        super(LoggerWorker, self).__init__()
        
        self._manager = manager
        self._period = manager.get_period()
        self._delay = manager.get_delay()

        self.micro_workers = list()

    def verify_workload(self):

        tags = self._manager.get_tags()

        if not tags:
            return False

        db = self._manager.get_db()

        if not db:
            return False

        return True

    def start_workers(self):

        # tags = self._manager.get_tags()
        # tags = list(chunks(tags, 3))
        log_table = self._manager.get_table()

        for period in log_table.get_groups():

            tags = log_table.get_tags(period)
            tags = list(chunks(tags, 3))
            
            for group in tags:
                # worker = MicroLoggerWorker(group, self._period)
                worker = MicroLoggerWorker(group, period)
                worker.daemon = True
                self.micro_workers.append(worker)

        for worker in self.micro_workers:
            worker.start()

    def stop(self):

        for worker in self.micro_workers:
            worker.stop()

        self.stop_event.set()

    def run(self):

        self._manager.init_database()
        
        if not self.verify_workload():
            return
        
        time.sleep(self._delay)

        try:    
            self.start_workers()     
            
            while True:

                if self.stop_event.is_set():
                    self.stop()
                    break
                
                time.sleep(0.5)

            logging.info("Logger worker shutdown successfully!")

        except Exception as e:
            message = "logger: Error on logger system"
            log_detailed(e, message)