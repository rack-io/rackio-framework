# -*- coding: utf-8 -*-
"""rackio/api/core.py

This module implements a hook class for decorating RackioResources.
"""

import falcon


class RackioHook:

    pass

rackio_hook = RackioHook()

rackio_hook.before = falcon.before
rackio_hook.after = falcon.after
