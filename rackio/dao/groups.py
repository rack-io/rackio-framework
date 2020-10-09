# -*- coding: utf-8 -*-
"""rackio/dao/groups.py

This module implements Groups Data Objects Access.
"""
from .core import RackioDAO


class GroupsDAO(RackioDAO):

    def get_all(self):

        return self.tag_engine.get_groups()

    def get(self, group_id):

        return self.tag_engine.serialize_group(group_id)