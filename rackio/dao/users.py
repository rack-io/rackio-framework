# -*- coding: utf-8 -*-
"""rackio/dao/users.py

This module implements Users Data Objects Access.
"""
from .core import RackioDAO

from ..dbmodels import User
from ..utils import serialize_dbo, hash_password
from playhouse.migrate import SqliteMigrator, MySQLMigrator, PostgresqlMigrator, migrate
from peewee import SqliteDatabase, MySQLDatabase, PostgresqlDatabase
from ..managers.logger import LoggerEngine
from peewee import CharField, TextField, DateField, DateTimeField, IntegerField, FloatField, BlobField, ForeignKeyField



class UsersDAO(RackioDAO):

    logger = LoggerEngine()

    def get_all(self):

        query = User.select()
        users = [user.username for user in query]

        return users

    def get_column_names(self):

        columns_dict = User._meta.fields
        return list(columns_dict.keys())

    def add_column(self, column_name, field, default, null=True):
        """
        Add a new column to any database.
        
        **Parameters:**

        * **table** (string): User Role.
        * **column_name** (string):
        * **field** (Peewee Field type)
        * **default** default value
        * **null** (bool): allow null values
        """
        db = self.logger.get_db()
        if isinstance(db, PostgresqlDatabase):

            migrator = PostgresqlMigrator(db)
        
        elif isinstance(db, SqliteDatabase):

            migrator = SqliteMigrator(db)

        elif isinstance(db, MySQLDatabase):

            migrator = MySQLMigrator(db)

        field = eval('{}Field(default={}, null={})'.format(field.capitalize(), default, null)) 

        migrate(
            migrator.add_column(
                'user',
                column_name,
                field
            )
        )

        result = {
            'message': 200
        }

        return result

    def add(self, username, password, role, **kwargs):

        result = None

        return result

    def set_license(self, username:str, license_type:str):
        r"""
        Documentation here
        """
        lic = hash_password(license_type)
        query = User.update(license_id=lic.index).where(User.username==username)
        query.execute()

        result = {
            'message': 200
        }
        return result

        