# -*- coding: utf-8 -*-
"""rackio/api/auth_hook.py

This module implements a hook class caller for decorating RackioResources.
"""
import falcon

from ..dao import AuthDAO


class Authorize(object):

    def __init__(self, roles):
        self._roles = roles

        self._auth = AuthDAO()

    def __call__(self, req, resp, resource, params):
        
        user = req.context['user']
        username = user['username']

        role = self._auth.get_role(username)

        if not role in self._roles:
            msg = "User is not authorize to access this area"
            raise falcon.HTTPForbidden("Unauthorize", msg)
