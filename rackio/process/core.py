# -*- coding: utf-8 -*-
"""rackio/workers/continuos.py

This module implements Core Rackio Process.
"""
import logging
import sys
import time

import concurrent.futures

from multiprocessing import Process


class CoreProcess(Process):
    
    def __init__(self, pipe):

        super(CoreProcess, self).__init__()

        self._pipe = pipe

        self.max_workers = 10
        self._logging_level = logging.INFO
        self._log_file = ""

        self._worker_functions = list()
        self._continous_functions = list()

        self._control_manager = None
        self._alarm_manager = None
        self._machine_manager = None
        self._function_manager = None
        
        self.db = None
        self._db_manager = LoggerEngine()

        self.workers = None

    def set_log(self, level=logging.INFO, file=""):
        """Sets the log file and level.
        
        # Parameters
        level (str): logging.LEVEL.
        file (str): filename to log.
        """

        self._logging_level = level
        
        if file:
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
    
        _db_worker = LoggerWorker(self._db_manager)
        _control_worker = ControlWorker(self._control_manager)
        _function_worker = FunctionWorker(self._function_manager)
        _machine_worker = StateMachineWorker(self._machine_manager)
        _alarm_worker = AlarmWorker(self._alarm_manager)

        try:

            workers = [
                _db_worker, 
                _control_worker, 
                _function_worker, 
                _machine_worker, 
                _alarm_worker,
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

    def _start_scheduler(self):
        
        _max = self.max_workers
        scheduler = concurrent.futures.ThreadPoolExecutor(max_workers=_max)

        try:

            for _f, period in self._worker_functions:

                try:
                    scheduler.submit(_f)
                except Exception as e:
                    error = str(e)
                    logging.error(error)

            for _f in self._continous_functions:

                try:
                    scheduler.submit(_f)
                except Exception as e:
                    error = str(e)
                    logging.error(error)

        except Exception as e:
            error = str(e)
            logging.error(error)

    def run(self):

        """Runs the main execution for the application to start serving.
        
        This will put all the components of the application at run

        # Example
    
        ```python
        >>> app.run()
        ```
        """

        self._start_logger()
        self._start_workers()
        self._start_scheduler()

        try:         
            while True:
                time.sleep(0.5)

        except (KeyboardInterrupt, SystemExit):
            logging.info("Manual Shutting down!!!")
            sys.exit()
    

