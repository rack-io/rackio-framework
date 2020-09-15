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

    def __init__(self, app, port=8000, mode=mode):

        super(APIWorker, self).__init__()

        self._api_app = app
        self._port = port
        self._mode = mode

    def run(self):

        if self._mode == "development":
            with make_server('', self._port, self._api_app, handler_class=CustomWSGIRequestHandler) as httpd:
                logging.info('Serving on port {}...'.format(self._port))
                httpd.serve_forever()
        else:
            serve(self._api_app, host='0.0.0.0', port=self._port)
