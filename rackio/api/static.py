# api/static.py

import os

from rackio import status_code


class StaticResource:
    def on_get(self, req, resp, folder, filename):
        resp.status = status_code.HTTP_200

        if ".css" in filename:
            resp.content_type = "text/css"
        elif ".js" in filename:
            resp.content_type = "application/javascript"
        else:
            resp.content_type = "appropriate/content-type"

        path = os.path.join(
            os.path.dirname(status_code.__file__), "static", folder, filename
        )

        with open(path, "r") as f:
            resp.body = f.read()
