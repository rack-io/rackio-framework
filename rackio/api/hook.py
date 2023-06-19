# -*- coding: utf-8 -*-
"""rackio/api/core.py

This module implements a hook class for decorating RackioResources.
"""

import falcon


class RackioHook:
    def __init__(self):
        self.before = falcon.before
        self.after = falcon.after


rackio_hook = RackioHook()
