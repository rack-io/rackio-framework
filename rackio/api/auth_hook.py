# -*- coding: utf-8 -*-
"""rackio/api/auth_hook.py

This module implements a hook class caller for decorating RackioResources.
"""
import falcon

from ..dao import AuthDAO
from ..core import Rackio

from .hook import rackio_hook


class Authorize(object):

    def __init__(self, roles):
        self._roles = roles

        self._auth = AuthDAO()

    def get_app(self):

        return Rackio()

    def __call__(self, req, resp, resource, params):

        app = self.get_app()

        if not app.auth_enabled():
            return
        
        try:
            user = req.context['user']
        except:
            msg = "User is not authenticated"
            raise falcon.HTTPForbidden("Unauthorized", msg)

        username = user['username']

        role = self._auth.get_role(username)

        if not role in self._roles:
            msg = "User is not authorize to access this area"
            raise falcon.HTTPForbidden("Unauthorized", msg)

def authorize(roles):

    auth = Authorize(roles)

    return rackio_hook.before(auth)
