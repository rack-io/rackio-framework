# -*- coding: utf-8 -*-
"""rackio/api/summary.py

This module implements all class Resources for the Alarm Manager.
"""

import json

from rackio import status_code

from .core import RackioResource


class AppSummaryResource(RackioResource):

    def on_get(self, req, resp):

        app = self.get_app()
        doc = app.summary()
        
        resp.body = json.dumps(doc, ensure_ascii=False)