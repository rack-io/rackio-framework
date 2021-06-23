# -*- coding: utf-8 -*-
"""rackio/workers/api.py

This module implements API Worker.
"""
import logging
from wsgiref.simple_server import make_server
from waitress import serve

from .worker import BaseWorker
from .handlers import CustomWSGIRequestHandler


class APIWorker(BaseWorker):

    def __init__(self, manager, port=8000, mode="development"):

        super(APIWorker, self).__init__()

        self._manager = manager
        self._port = port
        self._mode = mode

    def run(self):

        app = self._manager.app
        app.set_middleware()

        if self._mode == "development":
            with make_server('', self._port, app, handler_class=CustomWSGIRequestHandler) as httpd:
                logging.info('Development mode serving on port {}...'.format(self._port))
                httpd.serve_forever()
        else:
            logging.info('Production mode serving on port {}...'.format(self._port))
            serve(app, host='0.0.0.0', port=self._port)
