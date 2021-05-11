# -*- coding: utf-8 -*-
"""rackio/core.py

This module implements the core app class and methods for Rackio.
"""

import logging
import sys
import time
import concurrent.futures

from peewee import SqliteDatabase, MySQLDatabase, PostgresqlDatabase


from ._singleton import Singleton

from .config import RackioConfig

from .managers import LoggerManager
from .managers import AlarmManager
from .managers import ControlManager, FunctionManager
from .managers import StateMachineManager
from .managers import APIManager
from .managers import AuthManager

from .workers import AlarmWorker, APIWorker
from .workers import ControlWorker, FunctionWorker, LoggerWorker
from .workers import StateMachineWorker, _ContinuosWorker

from .web import RouteResource

from .utils import directory_paths, log_detailed, is_function, is_class

from .dbmodels import SQLITE, MYSQL, POSTGRESQL


class Rackio(Singleton):

    """Rackio main application class.

    This class is a singleton by inheritance, this makes
    it available in each module of an end application or
    code project

    Usage:

    ```python
    >>> from rackio import Rackio
    >>> app = Rackio()
    ```

    """

    def __init__(self, context=None):

        super(Rackio, self).__init__()
        
        self._context = context

        self.max_workers = 10
        self._logging_level = logging.INFO
        self._log_file = ""
        self._port = 8000
        self._mode = "development"

        self.config = RackioConfig()

        self._worker_functions = list()
        self._continous_functions = list()

        self._control_manager = ControlManager()
        self._alarm_manager = AlarmManager()
        self._machine_manager = StateMachineManager()
        self._function_manager = FunctionManager()
        self._api_manager = APIManager()
        self._db_manager = LoggerManager()
        
        self.db = None

        self.workers = None

    def set_port(self, port):

        self._port = port

    def set_mode(self, mode):

        self._mode = mode

    def get_mode(self):

        return self._mode
        
    def set_log(self, level=logging.INFO, file=""):
        """
        Sets the log file and level.
        
        **Parameters:**
        
        * **level** (str): `logging.LEVEL`.
        * **file** (str): log filename.

        **Returns:** `None`

        Usage:

        ```python
        >>> app.set_log(file="app.log")
        ```
        """

        self._logging_level = level
        
        if file:
            self._log_file = file

    def set_db(self, dbtype=SQLITE, drop_table=True, **kwargs):
        """
        Sets the database, it supports SQLite and Postgres,
        in case of SQLite, the filename must be provided.
        
        **Parameters:**

        * **dbfile** (str): a path to database file.
        * **kwargs**: Same attributes to a postgres connection.

        **Returns:** `None`

        Usage:

        ```python
        >>> app.set_db(dbfile="app.db")
        ```
        """

        from .dbmodels import proxy

        if dbtype == SQLITE:

            dbfile = kwargs.get("dbfile", ":memory:")
            
            self._db = SqliteDatabase(dbfile, pragmas={
                'journal_mode': 'wal',
                'journal_size_limit': 1024,
                'cache_size': -1024 * 64,  # 64MB
                'foreign_keys': 1,
                'ignore_check_constraints': 0,
                'synchronous': 0}
            )

        elif dbtype == MYSQL:
            
            app = kwargs['app']
            del kwargs['app']
            self._db = MySQLDatabase(app, **kwargs)

        elif dbtype == POSTGRESQL:
            
            app = kwargs['app']
            del kwargs['app']
            self._db = PostgresqlDatabase(app, **kwargs)
        
        proxy.initialize(self._db)
        self._db_manager.set_db(self._db)
        self._db_manager.set_dropped(drop_table)

    def set_workers(self, nworkers):
        """
        Sets the maximum workers in the ThreadPoolExecutor.
        
        **Parameters:**

        * **nworkers** (int): Number of workers.

        **Returns:** `None`
        """

        self.max_workers = nworkers

    def set_dbtags(self, tags, period=0.5, delay=1.0):
        """
        Sets the database tags for logging.
        
        **Parameters:**

        * **tags** (list): A list of the tags.

        **Returns:** `None`

        Usage:

        ```python
        >>> tags = ["P1", "P2", "T1"]
        >>> app.set_dbtags(tags, period=1.0)
        ```
        """

        self._db_manager.set_period(period)
        self._db_manager.set_delay(delay)

        for _tag in tags:
            self._db_manager.add_tag(_tag, period)

    def get_dbtags(self):
        """
        Returns the database tags for logging.
        """

        return self._db_manager.get_tags()

    def append_rule(self, rule):
        """
        Append a rule to the control manager.
        
        **Parameters:**

        * **rule** (`Rule`): a rule object.
        """

        self._control_manager.append_rule(rule)

    def get_rule(self, name):
        """
        Returns a Rule defined by its name.
        
        **Parameters:**
        
        * **name** (str): a rackio rule.
        """

        return self._control_manager.get_rule(name)

    def append_control(self, control):
        """
        Append a control to the control manager.
        
        **Parameters:**

        * **control** (`Control`): a control object.
        """

        self._control_manager.append_control(control)
    
    def get_control(self, name):
        """
        Returns a Control defined by its name.
        
        **Parameters:**

        * **name** (str): a rackio control.
        """

        return self._control_manager.get_control(name)

    def append_alarm(self, alarm):
        """
        Append an alarm to the alarm manager.
        
        **Parameters:**

        * **alarm** (`Alarm`): an alarm object.
        """

        self._alarm_manager.append_alarm(alarm)

    def get_alarm(self, name):
        """
        Returns a Alarm defined by its name.
        
        **Parameters:**

        * **name** (str): an alarm name.
        """

        alarm = self._alarm_manager.get_alarm(name)

        return alarm

    def get_alarm_by_tag(self, tag):
        """
        Returns a Alarm defined by its tag.

        **Parameters:**

        * **tag** (str): an alarm tag.
        """

        alarm = self._alarm_manager.get_alarm_by_tag(tag)

        return alarm

    def append_machine(self, machine, interval=1, mode="sync"):
        """
        Append a state machine to the state machine manager.
        
        **Parameters:**

        * **machine** (`RackioStateMachine`): a state machine object.
        * **interval** (int): Interval execution time in seconds.
        """
        machine.set_interval(interval)
        self._machine_manager.append_machine(machine, interval=interval, mode=mode)

    def get_machine(self, name):
        """
        Returns a Rackio State Machine defined by its name.
        
        **Parameters:**
        
        * **name** (str): a rackio state machine name.
        """

        return self._machine_manager.get_machine(name)

    def get_machines(self):
        """
        Returns All Rackio State Machine defined.
        """

        return self._machine_manager.get_machines()

    def define_machine(self, name="", interval=1, mode="sync", **kwargs):
        """
        Append a state machine to the state machine manager
        by a class decoration.
        
        **Parameters:**
        
        * **interval** (int): Interval execution time in seconds.
        """

        def decorator(cls):

            machine = cls(name, **kwargs)
            
            self.append_machine(machine, interval=interval, mode=mode)

            return cls

        return decorator

    def append_table(self, table):
        """
        Append a database model class definition.
        
        **Parameters:**

        * **table** (BaseModel): A Base Model Inheritance.
        """

        self._db_manager.register_table(table)

    def define_root(self, username, password):
        """
        Overrides the default Rackio root credentials.
        
        **Parameters:**

        * **username** (string): Root's username.
        * **password** (string): Root's password.
        """

        self._db_manager.set_root(username, password)

    def define_user(self, username, password, role="Operator", lic="None"):
        """
        Append a new user to allowed users in application.
        
        **Parameters:**

        * **username** (string): User's username.
        * **password** (string): User's password.
        * **role** (string): User's role (**Operator** by default).
        """

        self._db_manager.create_user(username, password, role, lic)

    def define_role(self, role):
        """
        Append a new user role to application.
        
        **Parameters:**

        * **role** (string): User Role.
        """

        self._db_manager.create_role(role)

    def define_system(self, system):
        """
        Append a new user role to application.
        
        **Parameters:**

        * **role** (string): User Role.
        """

        self._db_manager.create_system(system)

    def define_table(self, cls):
        """
        Append a database model class definition
        by a class decoration.
        """

        self.append_table(cls)

        return cls

    def get_manager(self, name):
        """
        Returns a specified application manager.
        
        **Parameters:**
        
        * **name** (str): a manager name.
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

        """
        Returns a Rackio Application Summary (dict).
        """

        result = dict()

        result["control_manager"] = self._control_manager.summary()
        result["data_logger"] = self._db_manager.summary()
        result["alarm_manager"] = self._alarm_manager.summary()
        result["machine_manager"] = self._machine_manager.summary()
        result["function_manager"] = self._function_manager.summary()

        return result

    def add_route(self, route, resource):
        """
        Append a resource and route the api.
        
        **Parameters:**

        * **route** (str): The url route for this resource.
        * **resource** (object): a url resouce template class instance.
        """

        if is_function(resource):
            _resource = RouteResource(resource)
            self._api_manager.add_route(route, _resource)
        else:
            self._api_manager.add_route(route, resource)

    def define_route(self, route, **kwargs):
        """
        Append a resource and route the api
        by a class decoration..
        
        **Parameters:**
        
        * **route** (str): The url route for this resource.
        """

        def decorator(cls):

            if is_class(cls):
                resource = cls(**kwargs)
            else:
                resource = cls
            
            self.add_route(route, resource)

            return cls

        return decorator

    def enable_auth(self):
        """
        Enables authentication mode in API.
        """

        self._api_manager.enable_auth()

    def disable_auth(self):
        """
        Disables authentication mode in API.
        """

        self._api_manager.disable_auth()

    def auth_enabled(self):
        """
        Return True is Authorization is enable, False otherwise.
        """

        self._api_manager.auth_enabled()

    def set_cors(self, allow_origins):
        """
        Sets the CORS origin rules.
        **Parameters:**
        * **allow_origins** (list): List of strings, all allowed origins.
        
        **Returns:** `None`

        Usage:
    
        ```python
        app.set_cors(['http://test.com:8080'])
        ```        
        """

        self._api_manager.set_cors(allow_origins)

    def get_cors(self):
        """
        Returns the CORS origin rules.
        **Parameters:**
        * **allow_origins** (list): List of strings, all allowed origins.
        
        **Returns:** `None`

        Usage:
    
        ```python
        app.get_cors()
        ```        
        """

        return self._api_manager.get_cors()

    def rackit(self, period):
        """
        Decorator method to register functions plugins.
        
        This method will register into the Rackio application
        a new function to be executed by the Thread Pool Executor

        **Parameters:**
        * **period** (float): Value of the default loop execution time.
        
        **Returns:** `None`

        Usage:
    
        ```python
        @app.rackit
        def hello():
            print("Hello!!!")
        ```        
        """

        def decorator(f):

            def wrapper():
                try:
                    f()
                except Exception as e:
                    error = str(e)
                    message = "{}:{}".format(f.__name__, error)
                    log_detailed(e, message)
                    
            _worker_function = (wrapper, period)
            self._worker_functions.append(_worker_function)
            return f
        
        return decorator

    def rackit_on(self, function=None, **kwargs):
        """
        Decorator to register functions plugins with continous execution.
        
        This method will register into the Rackio application
        a new function to be executed by the Thread Pool Executor

        **Parameters:**
        * **period** (float): Value of the default loop execution time, 
        if period is not defined `0.5` seconds is used by default.
        
        **Returns:** `None`

        Usage:
    
        ```python
        @app.rackit_on(period=0.5)
        def hello():
            print("Hello!!!")

        @app.rackit_on
        def hello_world():
            print("Hello World!!!")
        ```
        """
    
        if function:
            return _ContinuosWorker(function)
        else:

            def wrapper(function):
                return _ContinuosWorker(function, **kwargs)

            return wrapper

    def observe(self, tag):
        """
        Decorator method to register functions as tag observers.
        
        This method will register into the Rackio application
        a new function as a custom observer to be executed by 
        the Thread Pool Executor. If the tag associated changes 
        its value, the function registered will be executed.

        **Parameters:**
        * **tag** (str): Tag name.

        **Returns:** `None`

        Usage:
    
        ```python
        @app.observer
        def hello("T1"):
            print("Hello, Tag T1 has changed!!!")
        ```
        """

        def decorator(f):

            def wrapper():
                try:
                    f()
                except Exception as e:
                    error = str(e)
                    message = "{}:{}".format(f.__name__, error)
                    log_detailed(e, message)

            self._function_manager.append_function(tag, wrapper)
            return f
        
        return decorator

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
        _api_worker = APIWorker(self._api_manager, self._port, self._mode)

        try:

            workers = [
                _db_worker, 
                _control_worker, 
                _function_worker, 
                _machine_worker, 
                _alarm_worker, 
                _api_worker
            ]

            for worker in workers:

                worker.daemon = True
                worker.start()

        except Exception as e:
            message = "Error on wokers start-up"
            log_detailed(e, message)

        self.workers = workers

    def stop_workers(self):

        for worker in self.workers:
            try:
                worker.stop()
            except Exception as e:
                message = "Error on wokers stop"
                log_detailed(e, message)

    def _start_scheduler(self):
        
        _max = self.max_workers
        scheduler = concurrent.futures.ThreadPoolExecutor(max_workers=_max)

        for _f, period in self._worker_functions:

            try:
                scheduler.submit(_f)
            except Exception as e:
                message = "Error on functions worker start-up"
                log_detailed(e, message)

        for _f in self._continous_functions:

            try:
                scheduler.submit(_f)
            except Exception as e:
                message = "Error on continous functions worker start-up"
                log_detailed(e, message)

    def run(self, port=8000):
        """
        Runs the main execution for the application to start serving.
        
        This will put all the components of the application at run

        **Returns:** `None`

        Usage:
    
        ```python
        >>> app.run()
        ```
        """

        self.set_port(port)

        self._start_logger()
        self._start_workers()
        self._start_scheduler()

        try:         
            while True:
                time.sleep(0.5)

        except (KeyboardInterrupt, SystemExit):
            logging.info("Manual Shutting down!!!")
            self.stop_workers()
            time.sleep(0.5)

            sys.exit()
            