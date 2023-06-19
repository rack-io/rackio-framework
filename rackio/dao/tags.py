# -*- coding: utf-8 -*-
"""rackio/dao/tags.py

This module implements Tags Data Objects Access.
"""
from .core import RackioDAO


class TagsDAO(RackioDAO):
    def get_all(self):
        return self.tag_engine.serialize()

    def get(self, tag_id):
        return self.tag_engine.serialize_tag(tag_id)

    def write(self, tag_id, value):
        result = self.tag_engine.write_tag(tag_id, value)

        return result

    def get_history(self, tag_id):
        _logger = self.logger_engine

        history = _logger.read_tag(tag_id)

        waveform = dict()
        waveform["dt"] = history["dt"]
        waveform["t0"] = history["t0"]
        waveform["values"] = history["values"]

        return {"tag": tag_id, "waveform": waveform}

    def get_trend(self, tag_id, tstart, tstop):
        result = self.query_logger.query_trend(tag_id, tstart, tstop)

        return {"tag": tag_id, "waveform": result}

    def get_trends(self, tags, tstart, tstop):
        result = list()

        for tag in tags:
            waveform = self.query_logger.query_trend(tag, tstart, tstop)

            record = {"tag": tag, "waveform": waveform}

            result.append(record)

        return result

    def get_waveform(self, tag_id, tstart, tstop):
        result = self.query_logger.query_waveform(tag_id, tstart, tstop)

        return {"tag": tag_id, "waveform": result}

    def get_waveforms(self, tags, tstart, tstop):
        result = list()

        for tag in tags:
            waveform = self.query_logger.query_waveform(tag, tstart, tstop)

            record = {"tag": tag, "waveform": waveform}

            result.append(record)

        return result
