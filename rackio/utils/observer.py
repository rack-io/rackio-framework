# -*- coding: utf-8 -*-
"""rackio/utils/observer.py

This module implements Observer Utility Functions.
"""
import abc


class Observer(metaclass=abc.ABCMeta):
    """
    Define an updating interface for objects that should be notified of
    changes in a subject.
    """

    def __init__(self):
        self._subject = None
        self._observer_state = None

    @abc.abstractmethod
    def update(self, arg):
        pass