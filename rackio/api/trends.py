# -*- coding: utf-8 -*-
"""rackio/api/trends.py

This module implements all Trend Resources.
"""

import json

from .core import RackioResource
from .auth_hook import authorize

from ..dao import TagsDAO
from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, VISITOR_ROLE


class BaseResource(RackioResource):
    dao = TagsDAO()


class TrendResource(BaseResource):
    @authorize([SYSTEM_ROLE, ADMIN_ROLE, VISITOR_ROLE])
    def on_post(self, req, resp, tag_id):
        tstart = req.media.get("tstart")
        tstop = req.media.get("tstop")

        doc = self.dao.get_trend(tag_id, tstart, tstop)

        resp.body = json.dumps(doc, ensure_ascii=False)


class TrendCollectionResource(BaseResource):
    @authorize([SYSTEM_ROLE, ADMIN_ROLE, VISITOR_ROLE])
    def on_post(self, req, resp):
        tags = req.media.get("tags")

        tstart = req.media.get("tstart")
        tstop = req.media.get("tstop")

        result = self.dao.get_trends(tags, tstart, tstop)

        resp.body = json.dumps(result, ensure_ascii=False)
