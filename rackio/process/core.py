# -*- coding: utf-8 -*-
"""rackio/workers/continuos.py

This module implements Core Rackio Process.
"""

from multiprocessing import Process


class CoreProcess(Process):
    
    def __init__(self, context=None):

        super(CoreProcess, self).__init__()

        self._context = context

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

    def set_log(self, level=logging.INFO, file=""):
        """Sets the log file and level.
        
        # Parameters
        level (str): logging.LEVEL.
        file (str): filename to log.
        """

        self._logging_level = level
        
        if file:
            self._log_file = file

    def set_db(self, dbtype=SQLITE, drop_table=True, **kwargs):
        """Sets the database file.
        
        # Parameters
        dbfile (str): a path to database file.
        """

        from .dbmodels import proxy

        if dbtype == SQLITE:

            dbfile = kwargs.get("dbfile", ":memory:")
            
            self._db = SqliteDatabase(dbfile, pragmas={
                'journal_mode': 'wal',
                'cache_size': -1 * 64000,  # 64MB
                'foreign_keys': 1,
                'ignore_check_constraints': 0,
                'synchronous': 0}
            )

        elif dbtype == MYSQL:
            
            app = kwargs['app']
            self._db = MySQLDatabase(app, **kwargs)

        elif dbtype == POSTGRESQL:
            
            app = kwargs['app']
            self._db = PostgresqlDatabase(app, **kwargs)
        
        proxy.initialize(self._db)
        self._db_manager.set_db(self._db)
        self._db_manager.set_dropped(drop_table)

    def set_workers(self, nworkers):
        """Sets the maximum workers in the ThreadPoolExecutor.
        
        # Parameters
        nworkers (int): Number of workers.
        """

        self.max_workers = nworkers

    def set_dbtags(self, tags, period=0.5, delay=1.0, memory=None):
        """Sets the database tags for logging.
        
        # Parameters
        tags (list): A list of the tags.
        """

        self._db_manager.set_period(period)
        self._db_manager.set_delay(delay)

        if memory:
            self._db_manager.set_memory(memory)

        for _tag in tags:
            self._db_manager.add_tag(_tag)

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
    

