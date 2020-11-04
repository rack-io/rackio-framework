# -*- coding: utf-8 -*-

import falcon

from .utils import uri_to_path, get_static_path, get_content_type

from ..status_code import HTTP_200


class StaticResource:

    auth = {
        'auth_disabled': True
    }

    def on_get(self, req, resp, filename):

        uri = req.relative_uri
        
        path_stack = uri_to_path(uri)
        path = get_static_path(path_stack, filename)

        resp.status = falcon.HTTP_200
        resp.content_type = get_content_type(filename)

        try:
            with open(path, 'rb') as f:
                resp.body = f.read()
        except:
            with open(path, 'r', encoding='utf8', errors='ignore') as f:
                resp.body = f.read()


class RouteResource:

    auth = {
        'auth_disabled': True
    }

    def __init__(self, f):

        self._output_f = f

    def on_get(self, req, resp, **kwargs):

        content = self._output_f(**kwargs)

        resp.body = content
        resp.status = HTTP_200
        resp.content_type = 'text/html'