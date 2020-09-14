# -*- coding: utf-8 -*-
"""rackio/workers/continuos.py

This module implements API Rackio Process.
"""
import logging
import sys
import time

import concurrent.futures

from multiprocessing import Process

import falcon
from falcon_multipart.middleware import MultipartMiddleware

from ..web import StaticResource, resource_pairs

from ..api import TagResource, TagCollectionResource
from ..api import TagHistoryResource, TrendResource, TrendCollectionResource
from ..api import ControlResource, ControlCollectionResource
from ..api import RuleResource, RuleCollectionResource
from ..api import AlarmResource, AlarmCollectionResource
from ..api import EventCollectionResource
from ..api import AppSummaryResource
from ..api import BlobCollectionResource, BlobResource


class APIProcess(Process):
    
    def __init__(self, pipe, port=8000):

        super(APIProcess, self).__init__()

        self._pipe = pipe
        self._port = port
        self._api = api

    def set_api(self, api):

        self._api = api

    def set_port(self, port):
    
        self._port = port

    def set_log(self, level=logging.INFO, file=""):
        """Sets the log file and level.
        
        # Parameters
        level (str): logging.LEVEL.
        file (str): filename to log.
        """

        self._logging_level = level
        
        if "web_{}".format(file):
            self._log_file = file

    def _start_logger(self):
    
        log_format = "%(asctime)s:%(levelname)s:%(message)s"

        level = self._logging_level
        log_file = self._log_file

        if not log_file:
            logging.basicConfig(level=level, format=log_format)
            return
        
        logging.basicConfig(filename=log_file, level=level, format=log_format)

    def _start_workers(self):

        _api_worker = APIWorker(self._api, self._port)

        try:

            workers = [
                _api_worker
            ]

            for worker in workers:

                worker.daemon = True
                worker.start()

        except Exception as e:
            error = str(e)
            logging.error(error)

        self.workers = workers

    def stop_workers(self):

        for worker in self.workers:
            stop_event = worker.get_stop_event()
            stop_event.set()

    def run(self, port=8000):
    
        """Runs the main execution for the application to start serving.
        
        This will put all the components of the application at run

        # Example
    
        ```python
        >>> app.run()
        ```
        """

        self.set_port(port)

        self._start_logger()
        self._start_workers()

        try:         
            while True:
                time.sleep(0.5)

        except (KeyboardInterrupt, SystemExit):
            logging.info("Manual Shutting down!!!")
            sys.exit()
            