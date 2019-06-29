# -*- coding: utf-8 -*-
"""rackio/models.py

This module implements all class Resources for the RESTful API.
"""

import json

import falcon

from .engine import CVTEngine
from .logger import LoggerEngine


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
        _type = _cvt.read_type(tag_id)

        if _type == "float":
            value = float(value)
        elif _type == "int":
            value = int(value)
        elif _type == "bool":
            if value == "true":
                value = True
            elif value == "false":
                value = False
            else:
                value = bool(value)

        _cvt.write_tag(tag_id, value)

        doc = {
            'result': True
        }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)


class TagHistoryResource(object):

    def on_get(self, req, resp, tag_id):

        _logger = LoggerEngine()

        history = _logger.read_tag(tag_id)

        waveform = dict() 
        waveform["dt"] = history["dt"]
        waveform["t0"] = history["t0"].strftime('%Y-%m-%d %H:%M:%S')
        waveform["values"] = history["values"]

        doc = {
            'tag': tag_id,
            'waveform': waveform
        }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200
