# -*- coding: utf-8 -*-
"""rackio/api/users.py

This module implements all class Resources for User.
"""

import json

from rackio import status_code

from .core import RackioResource
from .auth_hook import authorize

from ..dao import UsersDAO
from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, VISITOR_ROLE


class BaseResource(RackioResource):
    
    dao = UsersDAO()


class UserCollectionResource(BaseResource):


    def on_get(self, req, resp):

        doc = self.dao.get_all()

        resp.body = json.dumps(doc, ensure_ascii=False)

class UsercolumnsCollectionResource(BaseResource):

    def on_get(self, req, resp):

        doc = self.dao.get_column_names()

        resp.body = json.dumps(doc, ensure_ascii=False)

class UserColumnResource(BaseResource):

    def on_post(self, req, resp, column_name):

        field = req.media.get('field')
        default = req.media.get('default')
        null = req.media.get('null')

        doc = self.dao.add_column(column_name, field, default, null)

        resp.body = json.dumps(doc, ensure_ascii=False)

class UserLicenseResource(BaseResource):

    def on_post(self, req, resp):

        username = req.media.get('username')
        license_type = req.media.get('license_type')

        doc = self.dao.set_license(username, license_type)

        resp.body = json.dumps(doc, ensure_ascii=False)
