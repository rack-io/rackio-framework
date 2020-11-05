# -*- coding: utf-8 -*-
"""rackio/api/tags.py

This module implements all class Resources for the Tag Engine.
"""

import json

from .core import RackioResource
from .auth_hook import authorize

from ..dao import LoggerDAO
from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, VISITOR_ROLE


class BaseResource(RackioResource):
    
    dao = LoggerDAO()


class LoggerResource(BaseResource):

    @authorize([SYSTEM_ROLE, ADMIN_ROLE])
    def on_get(self, req, resp):

        tags = self.dao.get_all()

        resp.body = json.dumps(tags, ensure_ascii=False)
