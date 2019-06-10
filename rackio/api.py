import json

import falcon


class TagResource(object):

    def on_get(self, req, resp):

        # tag_name = req["tag_name"]

        doc = {
            'tag': 'T1',
            'value': 23.44
        }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200
