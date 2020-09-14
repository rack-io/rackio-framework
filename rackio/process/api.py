# -*- coding: utf-8 -*-
"""rackio/workers/continuos.py

This module implements API Rackio Process.
"""

from multiprocessing import Process


class APIProcess(Process):
    
    def __init__(self, context=None):

        super(APIProcess, self).__init__()

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
            