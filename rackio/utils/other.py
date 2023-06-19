# -*- coding: utf-8 -*-
"""rackio/utils/other.py

This module implements other Use Utility Functions.
"""


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
