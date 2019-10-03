# -*- coding: utf-8 -*-
"""rackio/connection.py

This module implements all Rackio Instance Connections.
"""

WRITE = 0
READ = 1


class TagBinding:

    def __init__(self, local_tag, remote_tag, direction):

        self.local_tag = local_tag
        self.remote_tag = remote_tag
        self.direction = direction


class RackioBinding:

    def __init__(self, name, host_ip):

        self.name = name
        self.host_ip = host_ip
        self.tag_bindings = list()

    def append_binding(self, tag_binding):

        self.tag_bindings.append(tag_binding)

    