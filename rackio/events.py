# -*- coding: utf-8 -*-
"""rackio/events.py

This module defines the events history classes and function.
"""

from .models import Model, FloatField, IntegerField, BooleanField, StringField


class Event(Model):

    user = StringField()
    message = StringField()
    description = StringField()
    priority = IntegerField(default=4)
    datetime = StringField()
    
