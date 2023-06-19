# -*- coding: utf-8 -*-
"""rackio/dao/logger.py

This module implements Logger Data Objects Access.
"""
from .core import RackioDAO


class LoggerDAO(RackioDAO):
    def get_all(self):
        app = self.get_app()

        return app.get_dbtags()
