# -*- coding: utf-8 -*-
"""rackio/dbmodels.py

This module implements classes for
modelling the trending process.
"""
from datetime import datetime

from peewee import Model, CharField, TextField, DateTimeField, IntegerField, FloatField, ForeignKeyField

from .core import Rackio
app = Rackio()


class TagTrend(Model):

    name = CharField()
    start = DateTimeField()

    class Meta:

        database = app.db


class TagValue(Model):

    tag = ForeignKeyField(TagTrend, backref='values')
    value = FloatField()
    timestamp = DateTimeField()

    class Meta:

        database = app.db


class Event(Model):

    user = CharField()
    message = TextField()
    description = TextField()
    priority = IntegerField(default=4)
    date_time = DateTimeField()

    class Meta:

        database = app.db