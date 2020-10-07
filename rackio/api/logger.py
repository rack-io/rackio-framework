# -*- coding: utf-8 -*-
"""rackio/api/tags.py

This module implements all class Resources for the Tag Engine.
"""

import json

from .core import RackioResource
from ..dao import LoggerDAO


class BaseResource(RackioResource):
    
    dao = LoggerDAO()


class LoggerResource(BaseResource):

    def on_get(self, req, resp):

        tags = self.dao.get_all()

        resp.body = json.dumps(tags, ensure_ascii=False)
