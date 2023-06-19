# -*- coding: utf-8 -*-
"""rackio/api/auth_hook.py

This module implements a hook class caller for decorating RackioResources.
"""
import falcon

from functools import wraps

import json

from ..dao import AuthDAO

from .hook import rackio_hook


class Authorize(object):
    def __init__(self, roles):
        self._roles = roles
        self._auth = AuthDAO()

    def get_app(self):
        from ..core import Rackio

        return Rackio()

    def __call__(self, request, response, resource, params):
        app = self.get_app()
        if not app.auth_enabled():
            return

        username = request.media.get("username")

        role = self._auth.get_role(username)

        if not role in self._roles:
            msg = "User is not authorized to access this area"

            raise falcon.HTTPUnauthorized(title="Unauthorized", description=msg)


def authorize(roles):
    auth = Authorize(roles)

    return rackio_hook.before(auth)


class AuthToken(object):
    def __init__(self):
        self._auth = AuthDAO()

    def get_app(self):
        from ..core import Rackio

        return Rackio()

    def __call__(self, request, response, resource, params):
        app = self.get_app()

        if not app.auth_enabled():
            return

        token = request.headers["AUTHORIZATION"].split("Token ")[-1]

        if not self._auth.verify_key(token):
            msg = "User is not authenticated"

            raise falcon.HTTPUnauthorized(title="Unauthorized", description=msg)


auth_token = rackio_hook.before(AuthToken())


class AuthUserForm(object):
    def __init__(self):
        self._auth = AuthDAO()

    def get_app(self):
        from ..core import Rackio

        return Rackio()

    def __call__(self, request, response, resource, params):
        app = self.get_app()

        if not app.auth_enabled():
            return

        password = request.media.get("user_password")
        username = request.media.get("username")

        if not self._auth.verify_password(username, password):
            msg = "Invalid credentials"

            raise falcon.HTTPUnauthorized(title="Unauthorized", description=msg)


auth_user_form = rackio_hook.before(AuthUserForm())
