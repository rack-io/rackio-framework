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

LICENSE_ROOT = "System_Sudo"

ROOT_USER = "root"
ROOT_PASSWORD = "RackioRocks!"
ROOT_ROLE = SYSTEM_ROLE
ROOT_LICENSE = LICENSE_ROOT


class AuthManager:

    def __init__(self):

        self.auth = AuthDAO()
        self.ROLES = [SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE]
        self.ROLES += [OPERATOR_ROLE, VISITOR_ROLE]

        self.LICENSES = [LICENSE_ROOT]

        self.roles = list()
        self.users = list()
        self.licenses = list()

        self.root = (ROOT_USER, ROOT_PASSWORD, ROOT_ROLE, ROOT_LICENSE)
        self.license = (LICENSE_ROOT)

    def set_roles(self):

        for role in self.ROLES:

            self.auth.create_role(role)

    def set_licenses(self):

        for lic in self.LICENSES:

            self.auth.create_lic(lic)

    def set_root(self, root, password):

        self.root = (root, password, ROOT_ROLE, ROOT_LICENSE)

    def set_lic(self, lic):

        self.lic = lic

    def create_user(self, username, password, role, lic):

        self.users.append((username, password, role, lic))

    def create_role(self, role):

        self.roles.append(role)

    def create_license(self, lic):

        self.licenses.append(lic)

    def _create_user(self, username, password, role, lic):

        self.auth.create(role, lic, username=username, password=password)

    def _create_role(self, role):

        self.auth.create_role(role)

    def _create_license(self, lic):

        self.auth.create_lic(lic)

    def init_root(self):

        root, password, role, lic = self.root
        self._create_user(root, password, role, lic)

    def init_license(self):

        lic = self.lic
        self._create_license(lic)

    def init(self):

        self.set_licenses()
        self.set_roles()
        self.init_root()

        for lic in self.licenses:

            self._create_lic(lic)

        for role in self.roles:

            self._create_role(role)

        for username, password, role, lic in self.users:
            
            self._create_user(username, password, role, lic)
        