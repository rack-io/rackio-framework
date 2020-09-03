# rackio/workers/handlers.py

import logging

from wsgiref.simple_server import WSGIRequestHandler


class CustomWSGIRequestHandler(WSGIRequestHandler):

    def log_message(self, _format, *args):
        message =  "%s - - %s\n" % (self.client_address[0], _format % args)

        logging.info(message)
