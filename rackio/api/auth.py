# -*- coding: utf-8 -*-
"""rackio/api/auth.py

This module implements all class Resources for Authentication.
"""

import json

from rackio import status_code

from .core import RackioResource
from ..dao import AuthDAO


class BaseResource(RackioResource):
    
    dao = AuthDAO()


class LoginResource(BaseResource):

    def on_post(self, req, resp):

        username = req.media.get('value')
        password = req.media.get('value')

        self.dao.login(username, password)

        doc = "Login Successfully"
        
        resp.body = json.dumps(doc, ensure_ascii=False)
 

class LogoutResource(BaseResource):

    def on_get(self, req, resp, alarm_name):

        user = req.context['user']
        username = user['username']

        self.dao.logout(username)

        doc = "logout succesfully"

        resp.body = json.dumps(doc, ensure_ascii=False)