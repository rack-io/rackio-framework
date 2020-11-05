# -*- coding: utf-8 -*-
"""rackio/api/history.py

This module implements History Resources.
"""

import json

from .core import RackioResource
from .auth_hook import authorize

from ..dao import TagsDAO
from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, VISITOR_ROLE


class BaseResource(RackioResource):

    dao = TagsDAO()


class TagHistoryResource(BaseResource):

    @authorize([SYSTEM_ROLE, ADMIN_ROLE, VISITOR_ROLE])
    def on_get(self, req, resp, tag_id):

        doc = self.dao.get_history(tag_id)

        resp.body = json.dumps(doc, ensure_ascii=False)
    