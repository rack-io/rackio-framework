# -*- coding: utf-8 -*-
"""rackio/api/tags.py

This module implements all class Resources for the Tag Engine.
"""

import json

from .core import RackioResource
from ..dao import TagsDAO


class BaseResource(RackioResource):

    dao = TagsDAO()
    

class TagCollectionResource(BaseResource):

    def on_get(self, req, resp):

        doc = self.dao.get_all()

        resp.body = json.dumps(doc, ensure_ascii=False)


class TagResource(BaseResource):

    def on_get(self, req, resp, tag_id):

        doc = self.dao.get(tag_id)

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

        result = self.dao.write(tag_id, value)

        if result["result"]:

            doc = {
                'result': True
            }

        else:

            doc = {
                'result': False
            }
        
        resp.body = json.dumps(doc, ensure_ascii=False)


class TagHistoryResource(BaseResource):

    def on_get(self, req, resp, tag_id):

        doc = self.dao.get_history(tag_id)

        resp.body = json.dumps(doc, ensure_ascii=False)

    
class TrendResource(BaseResource):

    def on_post(self, req, resp, tag_id):

        tstart = req.media.get('tstart')
        tstop = req.media.get('tstop')

        doc = self.dao.get_trend(tag_id, tstart, tstop)

        resp.body = json.dumps(doc, ensure_ascii=False)


class TrendCollectionResource(BaseResource):

    def on_post(self, req, resp):

        tags = req.media.get('tags')

        tstart = req.media.get('tstart')
        tstop = req.media.get('tstop')
    
        result = self.dao.get_trends(tags, tstart, tstop)

        resp.body = json.dumps(result, ensure_ascii=False)


class WaveformResource(BaseResource):

    def on_post(self, req, resp, tag_id):

        tstart = req.media.get('tstart')
        tstop = req.media.get('tstop')

        doc = self.dao.get_waveform(tag_id, tstart, tstop)

        resp.body = json.dumps(doc, ensure_ascii=False)


class WaveformCollectionResource(BaseResource):

    def on_post(self, req, resp):

        tags = req.media.get('tags')

        tstart = req.media.get('tstart')
        tstop = req.media.get('tstop')
    
        result = self.dao.get_waveforms(tags, tstart, tstop)

        resp.body = json.dumps(result, ensure_ascii=False)
        