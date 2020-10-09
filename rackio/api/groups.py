# -*- coding: utf-8 -*-
"""rackio/api/groups.py

This module implements all class Resources for Groups in the Tag Engine.
"""

import json

from .core import RackioResource
from ..dao import GroupsDAO


class BaseResource(RackioResource):

    dao = GroupsDAO()
    

class GroupCollectionResource(BaseResource):

    def on_get(self, req, resp):

        doc = self.dao.get_all()

        resp.body = json.dumps(doc, ensure_ascii=False)


class GroupResource(BaseResource):

    def on_get(self, req, resp, group_id):

        doc = self.dao.get(group_id)

        resp.body = json.dumps(doc, ensure_ascii=False)

    