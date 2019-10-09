# -*- coding: utf-8 -*-
"""rackio/connection.py

This module implements all Rackio Instance Connections.
"""

WRITE = "write"
READ = "read"


class TagBinding:

    def __init__(self, local_tag, remote_tag, direction):

        self.local_tag = local_tag
        self.remote_tag = remote_tag
        self.direction = direction


class RackioBinding:

    def __init__(self, name, host_ip, host_port):

        self.name = name
        self.host_ip = host_ip
        self.host_port = host_port
        self.tag_bindings = list()

    def get_host(self):
        return self.host_ip, self.host_port

    def append_binding(self, tag_binding):

        self.tag_bindings.append(tag_binding)

    def get_bindings(self):

        return self.tag_bindings

    