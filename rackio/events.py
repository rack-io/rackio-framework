# -*- coding: utf-8 -*-
"""rackio/events.py

This module defines the events history classes and function.
"""

from .models import Model, IntegerField, BooleanField, StringField


class Event(Model):

    user = StringField()
    message = StringField()
    description = StringField(default="")
    classification = StringField()
    priority = IntegerField(default=4)
    date_time = StringField()
    
