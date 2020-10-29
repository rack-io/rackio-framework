# -*- coding: utf-8 -*-
"""rackio/logger/logdict.py

This module implements a dictionary based Class to hold
the tags to be logged.
"""


class LogTable(dict):

    def __init__(self):

        pass

    def validate(self, key, value):
        
        if type(key) != int:
            return False
        
        if type(value) != str:
            return False

        return True

    def assign_log(self, period, tag):

        pass

    def __setitem__(self, key, value):

        if not validate(key, value):
            return


    def __getitem__(self, key):

        pass