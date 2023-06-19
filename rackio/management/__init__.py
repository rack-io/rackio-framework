# -*- coding: utf-8 -*-

from .utilities import *


def execute_from_command_line(argv=None):
    """Run a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()
