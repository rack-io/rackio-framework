# -*- coding: utf-8 -*-
# rackio/api/dashboard.py

import os

from rackio import status_code


class DashboardResource(object):

    def on_get(self, req, resp):
        # do some sanity check on the filename
        
        resp.status = status_code.HTTP_200
        resp.content_type = 'text/html'
        
        path = os.path.join(os.path.dirname(status_code.__file__), "template", "dashboard.html")
        
        with open(path, 'r') as f:
            resp.body = f.read()


class DashboardViewResource(object):

    def on_get(self, req, resp, view):
        # do some sanity check on the filename
        
        resp.status = status_code.HTTP_200
        resp.content_type = 'text/html'
        
        path = os.path.join(os.path.dirname(status_code.__file__), 
            "dashboard",
            "views",
            "{}.html".format(view)
        )
        
        with open(path, 'r') as f:
            resp.body = f.read()


class DashboardPartialResource(object):

    def on_get(self, req, resp, partial):
        # do some sanity check on the filename
        
        resp.status = status_code.HTTP_200
        resp.content_type = 'text/html'
        
        path = os.path.join(os.path.dirname(status_code.__file__), 
            "dashboard",
            "views",
            "partials",
            "{}".format(partial)
        )
        
        with open(path, 'r') as f:
            resp.body = f.read()


class DashboardControllerResource(object):
    
    def on_get(self, req, resp, controller):
        # do some sanity check on the filename
        
        resp.status = status_code.HTTP_200

        resp.content_type = 'application/javascript'
        
        path = os.path.join(os.path.dirname(status_code.__file__),
            "dashboard",
            "controllers", 
            controller
        )

        with open(path, 'r') as f:
            resp.body = f.read()


class DashboardDirectiveResource(object):
    
    def on_get(self, req, resp, directive):
        # do some sanity check on the filename
        
        resp.status = status_code.HTTP_200

        resp.content_type = 'application/javascript'
        
        path = os.path.join(os.path.dirname(status_code.__file__),
            "dashboard",
            "components",
            "directives",
            directive
        )

        with open(path, 'r') as f:
            resp.body = f.read()


class DashboardServiceResource(object):
    
    def on_get(self, req, resp, service):
        # do some sanity check on the filename
        
        resp.status = status_code.HTTP_200

        resp.content_type = 'application/javascript'
        
        path = os.path.join(os.path.dirname(status_code.__file__),
            "dashboard",
            "components",
            "services",
            service
        )

        with open(path, 'r') as f:
            resp.body = f.read()


class DashboardStylesheetResource(object):
    
    def on_get(self, req, resp, stylesheet):
        # do some sanity check on the filename
        
        resp.status = status_code.HTTP_200

        resp.content_type = 'text/css'

        path = os.path.join(os.path.dirname(status_code.__file__),
            "dashboard",
            "stylesheets",
            stylesheet
            )

        with open(path, 'r') as f:
            resp.body = f.read()