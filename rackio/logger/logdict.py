# -*- coding: utf-8 -*-
"""rackio/logger/logdict.py

This module implements a dictionary based Class to hold
the tags to be logged.
"""


class LogTable(dict):

    def __init__(self):

        pass

    def validate(self, period, tag):
        
        if type(period) != int:
            return False
        
        if type(tag) != str:
            return False

        return True

    def add_tag(self, tag, period):

        if not self.validate(period, tag):
            return

        for key, value in self.items():

            if tag in value:
                self[key].remove(tag)

        if period in self.keys():

            self[period].append(tag)

        else:

            self[period] = [tag]

    def get_groups(self):

        return list(self.keys())

    def get_tags(self, group):

        return self[group]

    def get_all_tags(self):

        result = list()

        for group in self.get_groups():

            result += self.get_tags(group)

        return result

    def get_period(self, tag):

        for key, value in self.items():

            if tag in value:
                return key

    def serialize(self):

        return self
    
