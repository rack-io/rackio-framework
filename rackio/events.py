# -*- coding: utf-8 -*-
"""rackio/events.py

This module defines the events history classes and function.
"""

from .models import Model, IntegerType, StringType


class Event(Model):

    user = StringType()
    message = StringType()
    description = StringType(default="")
    classification = StringType()
    priority = IntegerType(default=4)
    date_time = StringType()
    
