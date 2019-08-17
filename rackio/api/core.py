# -*- coding: utf-8 -*-
"""rackio/api/core.py

This module implements all class Resources for the RESTful API.
"""

import json
import falcon

from rackio import status_code

from ..engine import CVTEngine
from ..logger import QueryLogger, LoggerEngine


class RackioResource(object):

    tag_engine = CVTEngine()
    logger_engine = LoggerEngine()
    query_logger = QueryLogger()
    
    def get_app(self):

        from ..core import Rackio

        return Rackio()
