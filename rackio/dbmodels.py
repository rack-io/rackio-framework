# -*- coding: utf-8 -*-
"""rackio/dbmodels.py

This module implements classes for
modelling the trending process.
"""
from datetime import datetime, date
from io import BytesIO
from .utils import hash_license, verify_license

from peewee import Proxy, Model, CharField, TextField, DateField, DateTimeField
from peewee import  IntegerField, FloatField, BlobField, ForeignKeyField, BooleanField

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
    period = FloatField()


class TagValue(BaseModel):

    tag = ForeignKeyField(TagTrend, backref='values')
    value = FloatField()
    timestamp = DateTimeField(default=datetime.now)


class Event(BaseModel):

    user = CharField()
    message = TextField()
    description = TextField()
    classification = TextField()
    priority = IntegerField(default=4)
    date_time = DateTimeField()


class Alarm(BaseModel):
    
    user = CharField()
    message = TextField()
    description = TextField()
    classification = TextField()
    priority = IntegerField(default=4)
    date_time = DateTimeField()
    name = TextField()
    state = TextField()


class Blob(BaseModel):

    name = CharField()
    blob = BlobField()

    @classmethod
    def get_value(cls, blob_name):

        blob = Blob.select().where(Blob.name==blob_name).get()
        blob = BytesIO(blob.blob)

        blob.seek(0)

        return blob.getvalue()


class UserRole(BaseModel):

    role = CharField()

class License(BaseModel):

    license = TextField()

    @classmethod
    def add(cls, license):
        r"""
        Documentation here
        """
        _lic = hash_license(lic)
        lic = License(license=_lic)
        lic.save()
    
    @classmethod
    def verify_license(cls, lic):
        
        user = User.get(username=username)

        if user:
            
            return True
        
        return False


class User(BaseModel):

    username = TextField(unique=True)
    password = TextField()
    role = ForeignKeyField(UserRole, backref='user')
    license = ForeignKeyField(License, backref='user')

    @staticmethod
    def verify_username(username):
        
        try:
            
            User.get(User.username==username)
            return True

        except:

            return False

    @classmethod
    def set_license(cls, username, lic):
        r"""
        Documentation here
        """
        _lic = hash_license(lic)
        license_id = License.select().where(License.license==_lic).get()
        query = cls.update(license=license_id).where(User.username==username)
        query.execute()


class Systems(BaseModel):

    system_name = TextField(unique=True)

    @classmethod
    def add(cls, system_name):
        r"""
        Create a new record in the Systems table
        """
        return Systems.create(system_name=system_name)
        

class Reliability(BaseModel):

    timestamp = DateTimeField(default=datetime.now)
    leak = BooleanField()
    true_false = BooleanField()
    false_true = BooleanField(default=False)
    system = ForeignKeyField(Systems)
    user = ForeignKeyField(User)

    @classmethod
    def add(cls, username, system_name, leak=True, true_false=False, false_true=False):
        r"""
        Create a new record in the Reliability table
        """
        user = User.get(username=username)
        system = Systems.get(system_name=system_name)

        return cls.create(
            user_id=user.id, 
            system_id=system.id,
            leak=leak,
            true_false=true_false,
            false_true=false_true
            )
    
    @classmethod
    def get_true_false(cls, start, stop):
        r"""
        Documentation here
        """
        pass

    @classmethod
    def get_leak(cls, start, stop):
        r"""
        Documentation here
        """

        pass

    @classmethod
    def get_false_true(cls, start, stop):
        r"""
        Documentation here
        """

        pass

    
# class Anomaly(BaseModel):

#     user = CharField()
#     instrument = TextField()
#     anomaly = TextField()
#     date_time = DateTimeField()

class Authentication(BaseModel):

    user = ForeignKeyField(User)
    key = TextField()

    expire = DateField(default=date.today)
