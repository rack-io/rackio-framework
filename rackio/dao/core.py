# -*- coding: utf-8 -*-
"""rackio/dao/core.py

This module implements Core Data Object.
"""

from ..engine import CVTEngine
from ..logger import QueryLogger, LoggerEngine


class RackioDAO:

    tag_engine = CVTEngine()
    logger_engine = LoggerEngine()
    query_logger = QueryLogger()
    
    def get_app(self):

        from ..core import Rackio

        return Rackio()