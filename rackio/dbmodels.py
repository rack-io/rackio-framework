# -*- coding: utf-8 -*-
"""rackio/dbmodels.py

This module implements classes for
modelling the trending process.
"""
from io import BytesIO

from peewee import Proxy, Model, CharField, TextField, DateTimeField, IntegerField, FloatField, BlobField, ForeignKeyField

proxy = Proxy()

SQLITE = 'sqlite'
MYSQL = 'mysql'
POSTGRESQL = 'postgresql'


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
    classification = TextField()
    priority = IntegerField(default=4)
    date_time = DateTimeField()


class Blob(BaseModel):

    name = CharField()
    blob = BlobField()

    @classmethod
    def get_value(self, blob_name):

        blob = Blob.select().where(Blob.name==blob_name).get()
        blob = BytesIO(blob.blob)

        blob.seek(0)

        return blob.getvalue()
