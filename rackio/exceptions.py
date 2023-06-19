# -*- coding: utf-8 -*-
"""rackio/exception.py

This module defines all exceptions handle by Rackio.
"""


class RackioError(Exception):
    """Base class for other exceptions"""

    pass


class InvalidTagNameError(RackioError):
    """Raised when an invalid tag name is defined"""

    pass


class TagNotFoundError(RackioError):
    """Raised when a Tag Name was not found in repository"""

    pass


class InvalidTagTypeError(RackioError):
    """Raised when a Tag is assigned a different type object"""

    pass


class WorkerError(RackioError):
    """Raised when an error occurs in a Continous Worker"""

    pass
