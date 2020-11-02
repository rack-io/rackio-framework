# -*- coding: utf-8 -*-
"""rackio/managers/auth.py

This module implements Authentication Manager.
"""

from ..dao import AuthDAO


class AuthManager:

    def __init__(self):

        self.auth = AuthDAO()
        self.ROLES = ["System", "Operator", "Supervisor"]

        self.roles = list()
        self.users = list()

    def set_roles(self):

        for role in self.ROLES:

            self.auth.create_role(role)

    def create_user(self, username, password, role):

        self.users.append((username, password, role))

    def create_role(self, role):

        self.roles.append(role)

    def _create_user(self, username, password, role):

        self.auth.create(role, username=username, password=password)

    def _create_role(self, role):

        self.auth.create_role(role)

    def init(self):

        self.set_roles()

        for role in self.roles:

            self._create_role(role)

        for username, password, role in self.users:
            
            self._create_user(username, password, role)
        