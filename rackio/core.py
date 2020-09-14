# -*- coding: utf-8 -*-
"""rackio/core.py

This module implements the core app class and methods for Rackio.
"""

import logging
import multiprocessing
import sys
import time
import concurrent.futures

from ._singleton import Singleton

from .utils import directory_paths

from .process import CoreProcess, APIProcess

from peewee import SqliteDatabase, MySQLDatabase, PostgresqlDatabase

from .logger import LoggerEngine

from .managers import AlarmManager
from .managers import ControlManager, FunctionManager
from .managers import StateMachineManager

from .workers import AlarmWorker, APIWorker
from .workers import ControlWorker, FunctionWorker, LoggerWorker
from .workers import StateMachineWorker, _ContinuosWorker

from ..dbmodels import SQLITE, MYSQL, POSTGRESQL



class Rackio(Singleton):

    """Rackio main application class.

    This class is a singleton by inheritance, this makes
    it available in each module of an end application or
    code project

    # Example

    ```python
    >>> from rackio import Rackio
    >>> app = Rackio()
    ```

    """

    def __init__(self, context=None):

        super(Rackio, self).__init__()
        
        self._context = context

        core_conn, api_conn = multiprocessing.Pipe()

        self._core_process = CoreProcess(core_conn)
        self._api_process = APIProcess(api_conn)

        self.max_workers = 10
        self._logging_level = logging.INFO
        self._log_file = ""
        self._port = 8000

        self._worker_functions = list()
        self._continous_functions = list()

        self._control_manager = ControlManager()
        self._alarm_manager = AlarmManager()
        self._machine_manager = StateMachineManager()
        self._function_manager = FunctionManager()
        
        self.db = None
        self._db_manager = LoggerEngine()

        self.workers = None

        self._init_api()
        self._init_web()

    def _init_api(self):
    
        self._api = falcon.API(middleware=[MultipartMiddleware()])

        _tag = TagResource()
        _tags = TagCollectionResource()
        _tag_history = TagHistoryResource()
        _tag_trend = TrendResource()
        _tag_trends = TrendCollectionResource()
        _control = ControlResource()
        _controls = ControlCollectionResource()
        _rule = RuleResource()
        _rules = RuleCollectionResource()
        _alarm = AlarmResource()
        _alarms = AlarmCollectionResource()
        _events = EventCollectionResource()
        _summary = AppSummaryResource()
        _blobs = BlobCollectionResource()
        _blob = BlobResource()

        self._api.add_route('/api/tags/{tag_id}', _tag)
        self._api.add_route('/api/tags', _tags)

        self._api.add_route('/api/history/{tag_id}', _tag_history)
        self._api.add_route('/api/trends/{tag_id}', _tag_trend)
        self._api.add_route('/api/trends', _tag_trends)

        self._api.add_route('/api/controls/{control_name}', _control)
        self._api.add_route('/api/controls', _controls)

        self._api.add_route('/api/rules/{rule_name}', _rule)
        self._api.add_route('/api/rules', _rules)
        
        self._api.add_route('/api/alarms/{alarm_name}', _alarm)
        self._api.add_route('/api/alarms', _alarms)

        self._api.add_route('/api/events', _events)

        self._api.add_route('/api/summary', _summary)

        self._api.add_route('/api/blobs', _blobs)
        self._api.add_route('/api/blobs/{blob_name}', _blob)

    def _init_web(self):

        web = self._api

        _static = StaticResource()

        pairs = resource_pairs()
        
        for path, route in pairs:

            route += "/{filename}"

            web.add_route(route, _static)

    def set_port(self, port):

        self._api_process.set_port(port)
        
    def set_log(self, level=logging.INFO, file=""):
        """Sets the log file and level.
        
        # Parameters
        level (str): logging.LEVEL.
        file (str): filename to log.
        """

        self._core_process.set_log(level=level, file=file)

    def set_db(self, dbtype=SQLITE, drop_table=True, **kwargs):
        """Sets the database file.
        
        # Parameters
        dbfile (str): a path to database file.
        """

        self._core_process.set_db(dbtype=dbtype, drop_table=drop_table, **kwargs)

    def set_workers(self, nworkers):
        """Sets the maximum workers in the ThreadPoolExecutor.
        
        # Parameters
        nworkers (int): Number of workers.
        """

        self._core_process.set_workers(nworkers)

    def set_dbtags(self, tags, period=0.5, delay=1.0, memory=None):
        """Sets the database tags for logging.
        
        # Parameters
        tags (list): A list of the tags.
        """

        self._core_process.set_dbtags(tags, period=period, delay=delay, memory=memory)

    def append_rule(self, rule):
        """Append a rule to the control manager.
        
        # Parameters
        rule (Rule): a rule object.
        """

        self._control_manager.append_rule(rule)

    def get_rule(self, name):
        """Returns a Rule defined by its name.
        
        # Parameters
        name (str): a rackio rule.
        """

        return self._control_manager.get_rule(name)

    def append_control(self, control):
        """Append a control to the control manager.
        
        # Parameters
        control (Control): a control object.
        """

        self._control_manager.append_control(control)
    
    def get_control(self, name):
        """Returns a Control defined by its name.
        
        # Parameters
        name (str): a rackio control.
        """

        return self._control_manager.get_control(name)

    def append_alarm(self, alarm):
        """Append an alarm to the alarm manager.
        
        # Parameters
        alarm (Alarm): an alarm object.
        """

        self._alarm_manager.append_alarm(alarm)

    def get_alarm(self, name):
        """Returns a Alarm defined by its name.
        
        # Parameters
        name (str): an alarm name.
        """

        alarm = self._alarm_manager.get_alarm(name)

        return alarm

    def append_machine(self, machine, interval=1):
        """Append a state machine to the state machine manager.
        
        # Parameters
        machine (RackioStateMachine): a state machine object.
        interval (int): Interval execution time in seconds.
        """

        self._machine_manager.append_machine(machine, interval=interval)

    def get_machine(self, name):
        """Returns a Rackio State Machine defined by its name.
        
        # Parameters
        name (str): a rackio state machine name.
        """

        return self._machine_manager.get_machine(name)

    def define_machine(self, name="", interval=1, **kwargs):

        """Append a state machine to the state machine manager
        by a class decoration.
        
        # Parameters
        interval (int): Interval execution time in seconds.
        """

        def decorator(cls):

            machine = cls(name, **kwargs)
            
            self.append_machine(machine, interval=interval)

            return cls

        return decorator

    def append_table(self, table):
        """Append a database model class definition.
        
        # Parameters
        table (BaseModel): A Base Model Inheritance.
        """

        self._db_manager.register_table(table)

    def define_table(self, cls):
        """Append a database model class definition
        by a class decoration.
        """

        self.append_table(cls)

        return cls

    def get_manager(self, name):
        """Returns a specified application manager.
        
        # Parameters
        name (str): a manager name.
        """

        if name == "control":
            manager = self._control_manager
        elif name == "alarm":
            manager = self._alarm_manager
        elif name == "state":
            manager = self._machine_manager
        else:
            manager = self._function_manager

        return manager

    def summary(self):

        """Returns a Rackio Application Summary (dict).
        """

        result = dict()

        result["control_manager"] = self._control_manager.summary()
        result["data_logger"] = self._db_manager.summary()
        result["alarm_manager"] = self._alarm_manager.summary()
        result["machine_manager"] = self._machine_manager.summary()
        result["function_manager"] = self._function_manager.summary()

        return result

    def add_route(self, route, resource):
        """Append a resource and route the api.
        
        # Parameters
        route (str): The url route for this resource.
        resource (object): a url resouce template class instance.
        """

        self._api.add_route(route, resource)

    def define_route(self, route, **kwargs):
        """Append a resource and route the api
        by a class decoration..
        
        # Parameters
        route (str): The url route for this resource.
        """

        def decorator(cls):

            resource = cls(**kwargs)
            
            self.add_route(route, resource)

            return cls

        return decorator

    def rackit(self, period):
        """Decorator method to register functions plugins.
        
        This method will register into the Rackio application
        a new function to be executed by the Thread Pool Executor

        # Example
    
        ```python
        @app.rackit
        def hello():
            print("Hello!!!")
        ```

        # Parameters
        period (float): Value of the default loop execution time.
        """

        def decorator(f):

            def wrapper():
                try:
                    f()
                except Exception as e:
                    error = str(e)
                    print("{}:{}".format(f.__name__, error))

            # _worker_function = (f, period)
            _worker_function = (wrapper, period)
            self._worker_functions.append(_worker_function)
            return f
        
        return decorator

    def rackit_on(self, function=None, **kwargs):
        """Decorator to register functions plugins with continous execution.
        
        This method will register into the Rackio application
        a new function to be executed by the Thread Pool Executor

        # Example
    
        ```python
        @app.rackit_on(period=0.5)
        def hello():
            print("Hello!!!")

        @app.rackit_on
        def hello_world():
            print("Hello World!!!")
        ```

        # Parameters
        period (float): Value of the default loop execution time, 
        if period is not defined 0.5 seconds is used by default.
        """
    
        if function:
            return _ContinuosWorker(function)
        else:

            def wrapper(function):
                return _ContinuosWorker(function, **kwargs)

            return wrapper

    def observe(self, tag):
        """Decorator method to register functions as tag observers.
        
        This method will register into the Rackio application
        a new function as a custom observer to be executed by 
        the Thread Pool Executor. If the tag associated changes 
        its value, the function registered will be executed.

        # Example
    
        ```python
        @app.observer
        def hello("T1"):
            print("Hello, Tag T1 has changed!!!")
        ```

        # Parameters
        tag (str): Tag name.
        """

        def decorator(f):

            def wrapper():
                try:
                    f()
                except Exception as e:
                    error = str(e)
                    print("{}:{}".format(f.__name__, error))

            self._function_manager.append_function(tag, wrapper)
            return f
        
        return decorator

    def _start_core(self):
        """
        Starts the core process by passing all the managers
        """
        self._core_process.

    def _start_api(self):
        """
        Starts the api process by passing the api.
        """
        pass

    def run(self, port=8000):

        """Runs the main execution for the application to start serving.
        
        This will put all the components of the application at run

        # Example
    
        ```python
        >>> app.run()
        ```
        """

        self.set_port(port)

        self._start_core()
        self._start_api()

        try:         
            while True:
                time.sleep(0.5)

        except (KeyboardInterrupt, SystemExit):
            logging.info("Manual Shutting down!!!")
            sys.exit()
            