# -*- coding: utf-8 -*-
"""rackio/api/__init__.py

This module implements all API initializations.
"""
from .tags import *
from .trends import *
from .waveforms import *
from .history import *
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
from .auth_hook import authorize, auth_token, auth_user_form
from .log_hook import log, notify_alarm_operation, notify_restart_systems, notify_transition
from .log_hook import notify_priority, notify_operation_mode
from .hook import rackio_hook
