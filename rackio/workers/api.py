# -*- coding: utf-8 -*-
"""rackio/workers/api.py

This module implements API Worker.
"""
import logging
from wsgiref.simple_server import make_server

from .worker import BaseWorker, ProcessWorker
from .handlers import CustomWSGIRequestHandler


class APIWorker(BaseWorker):

    def __init__(self, app, port=8000):

        super(APIWorker, self).__init__()

        self._api_app = app
        self._port = port

    def run(self):

        with make_server('', self._port, self._api_app, handler_class=CustomWSGIRequestHandler) as httpd:
            logging.info('Serving on port {}...'.format(self._port))
            httpd.serve_forever()


class APIProcess(ProcessWorker):
    
    def __init__(self, app, port=8000):

        super(APIProcess, self).__init__()

        self._api_app = app
        self._port = port

    def run(self):

        with make_server('', self._port, self._api_app, handler_class=CustomWSGIRequestHandler) as httpd:
            logging.info('Serving on port {}...'.format(self._port))
            httpd.serve_forever()
