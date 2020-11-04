# -*- coding: utf-8 -*-
"""rackio/managers/__init__.py

This module implements all Rackio Managers.
"""

from .logger import LoggerManager
from .alarms import AlarmManager
from .controls import ControlManager
from .functions import FunctionManager
from .state import StateMachineManager
from .api import APIManager

from .auth import AuthManager

from .auth import ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, VISITOR_ROLE

ROLES = [ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, VISITOR_ROLE]
