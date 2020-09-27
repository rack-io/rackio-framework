# -*- coding: utf-8 -*-
"""rackio/api/tags.py

This module implements all class Resources for the Tag Engine.
"""

import json

from .core import RackioResource


class LoggerResource(RackioResource):

    def on_get(self, req, resp):

        app = self.get_app()

        tags = app.get_dbtags()

        resp.body = json.dumps(tags, ensure_ascii=False)
