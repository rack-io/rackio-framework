# rackio/handlers.py

import logging

from wsgiref.simple_server import WSGIRequestHandler


class NoLoggingWSGIRequestHandler(WSGIRequestHandler):

    def log_message(self, format, *args):
        message =  "%s - - %s\n" % (self.client_address[0], format%args)

        logging.info(message)

