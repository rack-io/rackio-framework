# rackio/api/template.py

import os

from rackio import status_code


class TemplateResource(object):

    def on_get(self, req, resp, template):
        # do some sanity check on the filename
        
        resp.status = status_code.HTTP_200
        resp.content_type = 'text/html'
        
        path = os.path.join(os.path.dirname(status_code.__file__), "template", "{}.html".format(template))
        
        with open(path, 'r') as f:
            resp.body = f.read()