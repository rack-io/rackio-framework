# -*- coding: utf-8 -*-
# rackio/api/dashboard.py

import os

from jinja2 import Template

from rackio import status_code

from .config import rackio_modules, admin_modules
from .config import admin_directives, admin_services, admin_controllers

class AdminResource(object):

    def on_get(self, req, resp):
        
        resp.status = status_code.HTTP_200
        resp.content_type = 'text/html'
        
        path = os.path.join(os.path.dirname(status_code.__file__), "template", "admin.html")
        
        with open(path, 'r') as f:

            tm = Template(f.read())
            resp.body = tm.render(
                rackio_modules=rackio_modules, 
                admin_modules=admin_modules,
                directives=admin_directives,
                services=admin_services,
                controllers=admin_controllers
            )


class AdminViewResource(object):

    def on_get(self, req, resp, view):
        
        resp.status = status_code.HTTP_200
        resp.content_type = 'text/html'
        
        path = os.path.join(os.path.dirname(status_code.__file__), 
            "admin",
            "views",
            "{}.html".format(view)
        )
        
        with open(path, 'r') as f:
            resp.body = f.read()


class AdminPartialResource(object):

    def on_get(self, req, resp, partial):
        
        resp.status = status_code.HTTP_200
        resp.content_type = 'text/html'
        
        path = os.path.join(os.path.dirname(status_code.__file__), 
            "admin",
            "views",
            "partials",
            "{}".format(partial)
        )
        
        with open(path, 'r') as f:
            resp.body = f.read()


class AdminControllerResource(object):
    
    def on_get(self, req, resp, controller):
        
        resp.status = status_code.HTTP_200

        resp.content_type = 'application/javascript'
        
        path = os.path.join(os.path.dirname(status_code.__file__),
            "admin",
            "controllers", 
            controller
        )

        with open(path, 'r') as f:
            resp.body = f.read()


class AdminDirectiveResource(object):
    
    def on_get(self, req, resp, directive):
        
        resp.status = status_code.HTTP_200

        resp.content_type = 'application/javascript'
        
        path = os.path.join(os.path.dirname(status_code.__file__),
            "admin",
            "components",
            "directives",
            directive
        )

        with open(path, 'r') as f:
            resp.body = f.read()


class AdminServiceResource(object):
    
    def on_get(self, req, resp, service):
        
        resp.status = status_code.HTTP_200

        resp.content_type = 'application/javascript'
        
        path = os.path.join(os.path.dirname(status_code.__file__),
            "admin",
            "components",
            "services",
            service
        )

        with open(path, 'r') as f:
            resp.body = f.read()


class AdminStylesheetResource(object):
    
    def on_get(self, req, resp, stylesheet):
        
        resp.status = status_code.HTTP_200

        resp.content_type = 'text/css'

        path = os.path.join(os.path.dirname(status_code.__file__),
            "admin",
            "stylesheets",
            stylesheet
            )

        with open(path, 'r') as f:
            resp.body = f.read()