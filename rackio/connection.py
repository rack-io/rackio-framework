# -*- coding: utf-8 -*-
"""rackio/connection.py

This module implements all Rackio Instance Connections.
"""
import requests
import json

WRITE = 0
READ = 1


class TagBinding:

    def __init__(self, local_tag, remote_tag, direction):

        self.local_tag = local_tag
        self.remote_tag = remote_tag
        self.direction = direction

    def sync(self, host, port):

        if self.direction == "read":
            
            url = "http://{}:{}/api/tags/{}".format(host, port, self.remote_tag)
            
            response = requests.get(url)
            response = json.loads(response.content)

        elif self.direction == "write":

            value = 45.4
            
            url = "http://{}:{}/api/tags/{}".format(host, port, self.remote_tag)
            
            response = requests.post('', json={"value": value})

        if response.status_code == 200:

            return True
        else:
            return False



class RackioBinding:

    def __init__(self, name, host_ip):

        self.name = name
        self.host_ip = host_ip
        self.tag_bindings = list()

    def append_binding(self, tag_binding):

        self.tag_bindings.append(tag_binding)

    