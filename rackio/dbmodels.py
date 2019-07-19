# -*- coding: utf-8 -*-
"""rackio/dbmodels.py

This module implements classes for
modelling the trending process.
"""
from datetime import datetime

from peewee import Proxy, Model, CharField, TextField, DateTimeField, IntegerField, FloatField, ForeignKeyField

proxy = Proxy()

class BaseModel(Model):
    class Meta:
        database = proxy


class TagTrend(BaseModel):

    name = CharField()
    start = DateTimeField()


class TagValue(BaseModel):

    tag = ForeignKeyField(TagTrend, backref='values')
    value = FloatField()
    timestamp = DateTimeField()


class Event(BaseModel):

    user = CharField()
    message = TextField()
    description = TextField()
    priority = IntegerField(default=4)
    date_time = DateTimeField()
