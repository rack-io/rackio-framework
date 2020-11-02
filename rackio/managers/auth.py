# -*- coding: utf-8 -*-
"""rackio/managers/auth.py

This module implements Authentication Manager.
"""

from ..dao import AuthDAO


class AuthManager:

    def __init__(self):

        self.auth = AuthDAO()
        self.ROLES = ["System", "Operator", "Supervisor"]

    def set_roles(self):

        for role in self.ROLES:

            self.auth.create_role(role)

    def create_user(self, username, password, role):

        self.auth.create(role, username=username, password=password)

    def create_role(self, role):

        self.auth.create_role(role)

    