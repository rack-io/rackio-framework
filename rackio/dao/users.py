# -*- coding: utf-8 -*-
"""rackio/dao/users.py

This module implements Users Data Objects Access.
"""
from .core import RackioDAO

from ..dbmodels import User
from ..utils import serialize_dbo


class UsersDAO(RackioDAO):

    def get_all(self):

        query = User.select()
        users = [user.username for user in query]

        return users

    def add(self, username, password, role, **kwargs):

        result = None

        return result
        