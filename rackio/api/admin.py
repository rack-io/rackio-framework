# api/static.py

import os

from rackio import status_code


class AdminResource(object):

    def on_get(self, req, resp):
        # do some sanity check on the filename
        
        resp.status = status_code.HTTP_200
        resp.content_type = 'text/html'
        
        # path = "template/{}".format(template)
        path = os.path.join(os.path.dirname(status_code.__file__), "template", "admin.html")
        
        with open(path, 'r') as f:
            resp.body = f.read()