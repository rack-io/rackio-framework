# -*- coding: utf-8 -*-
"""rackio/api/users.py

This module implements all class Resources for User.
"""

import json
from datetime import datetime

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

    