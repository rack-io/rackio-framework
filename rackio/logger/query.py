# -*- coding: utf-8 -*-
"""rackio/logger/query.py

This module implements a QueryLogger layer class,
to retrieve history, trends and waveforms from database.
"""

from datetime import datetime, timedelta

from .engine import LoggerEngine
from ..dbmodels import TagTrend, TagValue

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
OUTPUT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class QueryLogger:

    def __init__(self):

        self._logger = LoggerEngine()

    def get_values(self, tag):

        query = TagTrend.select().order_by(TagTrend.start.desc())
        trend = query.where(TagTrend.name == tag).get()
        values = trend.values
        
        return values

    def get_period(self, tag):

        query = TagTrend.select().order_by(TagTrend.start.desc())
        trend = query.where(TagTrend.name == tag).get()
        
        return trend.period

    def get_start(self, tag):

        query = TagTrend.select().order_by(TagTrend.start.desc())
        trend = query.where(TagTrend.name == tag).get()
        
        return trend.start

    def query_waveform(self, tag, start, stop):

        _query = TagTrend.select().order_by(TagTrend.start)
        trend = _query.where(TagTrend.name == tag).get()
        
        start = datetime.strptime(start, DATETIME_FORMAT)
        stop = datetime.strptime(stop, DATETIME_FORMAT)

        period = trend.period
        
        _query = trend.values.select().order_by(TagValue.timestamp.asc())
        values = _query.where((TagValue.timestamp > start) & (TagValue.timestamp < stop))
        
        result = dict()

        t0 = values[0].timestamp.strftime(DATETIME_FORMAT)
        values = [value.value for value in values]

        result["t0"] = t0
        result["dt"] = period
        
        result["values"] = values

        return result

    def query_trend(self, tag, start, stop):

        _query = TagTrend.select().order_by(TagTrend.start)
        trend = _query.where(TagTrend.name == tag).get()
        
        start = datetime.strptime(start, DATETIME_FORMAT)
        stop = datetime.strptime(stop, DATETIME_FORMAT)
        
        _query = trend.values.select().order_by(TagValue.timestamp.asc())
        values = _query.where((TagValue.timestamp > start) & (TagValue.timestamp < stop))
        
        result = dict()

        values = [{"x": value.timestamp.strftime(OUTPUT_DATETIME_FORMAT), "y": value.value} for value in values]

        result["values"] = values

        return result

    def query_last(self, tag, seconds=None, values=None, waveform=False):

        if seconds:

            stop = datetime.now()
            start = stop - timedelta(seconds=seconds)

            start = start.strftime(DATETIME_FORMAT)
            stop = stop.strftime(DATETIME_FORMAT)

            if waveform:

                return self.query_waveform(tag, start, stop)

            return self.query_trend(tag, start, stop)

        if values:

            period = self.get_period(tag)

            stop = datetime.now()
            start = stop - values * timedelta(seconds=period)

            start = start.strftime(DATETIME_FORMAT)
            stop = stop.strftime(DATETIME_FORMAT)

            if waveform:
                return self.query_waveform(tag, start, stop)
            
            return self.query_trend(tag, start, stop)

    def query_first(self, tag, seconds=None, values=None, waveform=False):

        tag_values = self.get_values(tag)

        if seconds:

            start = tag_values[0].timestamp
            stop = start + seconds

            start = start.strftime(DATETIME_FORMAT)
            stop = stop.strftime(DATETIME_FORMAT)

            if waveform:
                return self.query_waveform(tag, start, stop)
            
            return self.query_trend(tag, start, stop)

        if values:

            period = self.get_period(tag)

            start = self.get_start(tag)
            stop = start + values * timedelta(seconds=period)

            start = start.strftime(DATETIME_FORMAT)
            stop = stop.strftime(DATETIME_FORMAT)

            if waveform:
                return self.query_waveform(tag, start, stop)
            
            return self.query_trend(tag, start, stop)
