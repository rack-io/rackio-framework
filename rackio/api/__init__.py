# -*- coding: utf-8 -*-
"""rackio/api/__init__.py

This module implements all API initializations.
"""
from .tags import *
from .groups import *
from .controls import *
from .alarms import *
from .events import *
from .workers import *
from .static import *
from .summary import *
from .blobs import *
from .logger import *

from .auth import *

from .hook import rackio_hook
from .auth_hook import Authorize
