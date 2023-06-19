# -*- coding: utf-8 -*-
"""rackio/utils/inspect.py

This module implements Object Inspection Utility Functions.
"""
import inspect
import logging
import types


def log_detailed(e, message):
    logging.error(message)
    logging.error(e, exc_info=True)


def is_function(f):
    return isinstance(f, types.FunctionType)


def is_class(cls):
    return inspect.isclass(cls)
