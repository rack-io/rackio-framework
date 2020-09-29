# -*- coding: utf-8 -*-
"""rackio/workers/logger.py

This module implements Logger Worker.
"""
import time
import logging

from .worker import BaseWorker
from ..logger import LoggerEngine


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

    def init_database(self):

        if self._manager.get_dropped():
            try:
                self._manager.drop_tables()
            except Exception as e:
                error = str(e)
                logging.error("Database:{}".format(error))

        self._manager.create_tables()

    def set_tags(self):

        tags = self._manager.get_tags()
        
        for tag in tags:

            self._manager.set_tag(tag)

    def write_tags(self):

        for _tag in self._manager.get_tags():
            value = self.tag_engine.read_tag(_tag)
            self._manager.write_tag(_tag, value)

    def start_workers(self):

        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        tags = self._manager.get_tags()
        tags = list(chunks(tags, 3))

        for group in tags:
            worker = MicroLoggerWorker(group, self._period)
            worker.daemon = True
            self.micro_workers.append(worker)

        for worker in self.micro_workers:
            worker.start()

    def stop(self):

        for worker in self.micro_workers:
            worker.stop()

        self.stop_event.set()

    def run(self):

        self.init_database()
        
        if not self.verify_workload():
            return
            
        self.set_tags()
        
        time.sleep(self._delay)

        try:    
            self.start_workers()     
            
            while True:

                if self.stop_event.is_set():
                    self.stop()
                    break
                
                time.sleep(0.5)

        except Exception as e:
            pass

        # time.sleep(self._period)

        # self.set_last()

        # while True:

        #     self.write_tags()
        #     self.sleep_elapsed() 