# -*- coding: utf-8 -*-
"""rackio/models.py

This module implements a Tags and other classes for
modelling the subjects involved in the core of the engine.
"""
from .utils import Observer


class Tag:

    def __init__(self, name, value, _type):

        self.name = name
        self.value = value
        self._type = _type

        self._observers = set()

    def set_value(self, value):

        self.value = value
        self.notify()
    
    def get_value(self):
        
        return self.value

    def get_type(self):
        
        return self._type
    
    def attach(self, observer):

        observer._subject = self
        self._observers.add(observer)

    def detach(self, observer):

        observer._subject = None
        self._observers.discard(observer)

    def notify(self):

        for observer in self._observers:

            observer.update()


class TagObserver(Observer):
    """
    Implement the Observer updating interface to keep its state
    consistent with the subject's.
    Store state that should stay consistent with the subject's.
    """
    def __init__(self, tag_queue):

        super(TagObserver, self).__init__()
        self._tag_queue = tag_queue

    def update(self):

        """
        This methods inserts the changing Tag into a 
        Producer-Consumer Queue Design Pattern
        """
        
        result = dict()

        result["tag"] = self._subject.name
        result["value"] = self._subject.value

        self._tag_queue.put(result)


class Model:
    """
    Implements an Abstact Model to inherit for custom models
    creation
    """

    def __init__(self, **kwargs):

        pass

    def commit(self):

        pass

    def get(self, tag):

        pass