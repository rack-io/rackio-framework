import json

import falcon

from .engine import CVTEngine


class TagCollectionResource(object):

    def on_get(self, req, resp):

        doc = list()

        _cvt = CVTEngine()
        tags = _cvt.get_tags()

        print("TAGS", tags)

        for _tag in tags:

            value = _cvt.read_tag(_tag)

            result = {
                'tag': _tag,
                'value': value
            }

            doc.append(result)

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200


class TagResource(object):

    def on_get(self, req, resp, tag_id):

        _cvt = CVTEngine()

        value = _cvt.read_tag(tag_id)

        doc = {
            'tag': tag_id,
            'value': value
        }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, tag_id):
        
        value = req.media.get('value')

        _cvt = CVTEngine()
        _cvt.write_tag(tag_id, value)

        doc = {
            'result': True
        }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)
