# -*- coding: utf-8 -*-
"""rackio/api/licenses.py

This module implements all class Resources for License.
"""

import json

from rackio import status_code

from .core import RackioResource
from .auth_hook import authorize

from ..dao import LicensesDAO

class LicenseResource(RackioResource):

    def on_post(self, req, resp):

        _license = req.media.get('license')

        doc = self.dao.add(_license)

        resp.body = json.dumps(doc, ensure_ascii=False)