# -*- coding: utf-8 -*-
"""rackio/api/summary.py

This module implements all class Resources for the Alarm Manager.
"""

import json

from .core import RackioResource
from .auth_hook import authorize

from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, VISITOR_ROLE


class AppSummaryResource(RackioResource):
    @authorize([SYSTEM_ROLE, ADMIN_ROLE, VISITOR_ROLE])
    def on_get(self, req, resp):
        app = self.get_app()
        doc = app.summary()

        resp.body = json.dumps(doc, ensure_ascii=False)
