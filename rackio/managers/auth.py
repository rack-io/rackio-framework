# -*- coding: utf-8 -*-
"""rackio/managers/auth.py

This module implements Authentication Manager.
"""

from ..dao import AuthDAO

SYSTEM_ROLE = "System"
ADMIN_ROLE = "Admin"
SUPERVISOR_ROLE = "Supervisor"
OPERATOR_ROLE = "Operator"
VISITOR_ROLE = "Visitor"

ROOT_USER = "root"
ROOT_PASSWORD = "RackioRocks!"
ROOT_ROLE = SYSTEM_ROLE


class AuthManager:

    def __init__(self):

        self.auth = AuthDAO()
        self.ROLES = [SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE]
        self.ROLES += [OPERATOR_ROLE, VISITOR_ROLE]

        self.roles = list()
        self.users = list()

        self.root = (ROOT_USER, ROOT_PASSWORD, ROOT_ROLE)

    def set_roles(self):

        for role in self.ROLES:

            self.auth.create_role(role)

    def set_root(self, root, password):

        self.root = (root, password, ROOT_ROLE)

    def create_user(self, username, password, role):

        self.users.append((username, password, role))

    def create_role(self, role):

        self.roles.append(role)

    def _create_user(self, username, password, role):

        self.auth.create(role, username=username, password=password)

    def _create_role(self, role):

        self.auth.create_role(role)

    def init_root(self):

        root, password, role = self.root
        self._create_user(root, password, role)

    def init(self):

        self.set_roles()
        self.init_root()

        for role in self.roles:

            self._create_role(role)

        for username, password, role in self.users:
            
            self._create_user(username, password, role)
        