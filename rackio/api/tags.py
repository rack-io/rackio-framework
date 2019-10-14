# -*- coding: utf-8 -*-
"""rackio/api/tags.py

This module implements all class Resources for the Tag Engine.
"""

import json

from rackio import status_code

from .core import RackioResource


class TagCollectionResource(RackioResource):

    def on_get(self, req, resp):

        doc = list()

        _cvt = self.tag_engine
        tags = _cvt.get_tags()

        for _tag in tags:

            value = _cvt.read_tag(_tag)
            
            try:
                result = {
                    'tag': _tag,
                    'value': value._serialize()
                }
            except:
                result = {
                    'tag': _tag,
                    'value': value
                }

            doc.append(result)

        resp.body = json.dumps(doc, ensure_ascii=False)


class TagResource(RackioResource):

    def on_get(self, req, resp, tag_id):

        _cvt = self.tag_engine

        value = _cvt.read_tag(tag_id)

        try:
            doc = {
                'tag': tag_id,
                'value': value._serialize()
            }
        except:
            doc = {
                'tag': tag_id,
                'value': value
            }

        resp.body = json.dumps(doc, ensure_ascii=False)

    def on_post(self, req, resp, tag_id):
        
        value = req.media.get('value')

        _cvt = self.tag_engine
        _type = _cvt.read_type(tag_id)

        if not "." in tag_id:
            if _type == "float":
                value = float(value)
            elif _type == "int":
                value = int(value)
            elif _type == "str":
                value = str(value)
            elif _type == "bool":
                if value == "true":
                    value = True
                elif value == "false":
                    value = False
                else:
                    value = bool(value)

        result = _cvt.write_tag(tag_id, value)

        if result["result"]:

            doc = {
                'result': True
            }

        else:

            doc = {
                'result': False
            }
        
        resp.body = json.dumps(doc, ensure_ascii=False)



class TagHistoryResource(RackioResource):

    def on_get(self, req, resp, tag_id):

        _logger = self.logger_engine

        history = _logger.read_tag(tag_id)

        waveform = dict() 
        waveform["dt"] = history["dt"]
        waveform["t0"] = history["t0"]
        waveform["values"] = history["values"]

        doc = {
            'tag': tag_id,
            'waveform': waveform
        }

        resp.body = json.dumps(doc, ensure_ascii=False)

    
class TrendResource(RackioResource):

    def on_post(self, req, resp, tag_id):

        tstart = req.media.get('tstart')
        tstop = req.media.get('tstop')

        _query_logger = self.query_logger
        result = _query_logger.query(tag_id, tstart, tstop)

        doc = {
            'tag': tag_id,
            'waveform': result
        }

        resp.body = json.dumps(doc, ensure_ascii=False)
        