# -*- coding: utf-8 -*-
"""rackio/logger/query.py

This module implements a QueryLogger layer class,
to retrieve history, trends and waveforms from database.
"""

from datetime import datetime, timedelta

from .engine import LoggerEngine
from ..dbmodels import TagTrend, TagValue
from peewee import Expression
from peewee import fn

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
OUTPUT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
SAMPLING_TIME = 1 # SECONDS


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

    def query_waveform(self, tag, start, stop, sampling_time=SAMPLING_TIME):

        _query = TagTrend.select().order_by(TagTrend.start)
        trend = _query.where(TagTrend.name == tag).get()
        
        start = datetime.strptime(start, DATETIME_FORMAT)
        stop = datetime.strptime(stop, DATETIME_FORMAT)

        period = trend.period
        sampling = int(sampling_time / period)
        
        _query = trend.values.select().order_by(TagValue.timestamp.asc())
        values = _query.where((TagValue.timestamp > start) & (TagValue.timestamp < stop))
        
        result = dict()

        t0 = values[0].timestamp.strftime(DATETIME_FORMAT)
        values = [value.value for count, value in enumerate(values) if count % sampling == 0]

        result["t0"] = t0
        result["dt"] = period
        
        result["values"] = values

        return result

    def query_trend(self, tag, start, stop, sampling_time=SAMPLING_TIME):

        _query = TagTrend.select().order_by(TagTrend.start)
        trend = _query.where(TagTrend.name == tag).get()
        
        start = datetime.strptime(start, DATETIME_FORMAT)
        stop = datetime.strptime(stop, DATETIME_FORMAT)

        period = self.get_period(tag)
        sampling = int(sampling_time / period)
        
        _query = trend.values.select().order_by(TagValue.timestamp.asc())
        values = _query.where((TagValue.timestamp > start) & (TagValue.timestamp < stop))

        result = dict()

        values = [{"x": value.timestamp.strftime(OUTPUT_DATETIME_FORMAT), "y": value.value} for count, value in enumerate(values) if count % sampling == 0]

        result["values"] = values

        return result

    def query_last(self, tag, seconds=None, values=None, waveform=False, sampling_time=1):

        if seconds:

            stop = datetime.now()
            start = stop - timedelta(seconds=seconds)

            start = start.strftime(DATETIME_FORMAT)
            stop = stop.strftime(DATETIME_FORMAT)

            if waveform:

                return self.query_waveform(tag, start, stop, sampling_time=sampling_time)

            return self.query_trend(tag, start, stop, sampling_time=sampling_time)

        if values:

            period = self.get_period(tag)

            stop = datetime.now()
            start = stop - values * timedelta(seconds=period)

            start = start.strftime(DATETIME_FORMAT)
            stop = stop.strftime(DATETIME_FORMAT)

            if waveform:
                return self.query_waveform(tag, start, stop, sampling_time=sampling_time)
            
            return self.query_trend(tag, start, stop, sampling_time=sampling_time)

    def query_first(self, tag, seconds=None, values=None, waveform=False, sampling_time=1):

        tag_values = self.get_values(tag)

        if seconds:

            start = tag_values[0].timestamp
            stop = start + seconds

            start = start.strftime(DATETIME_FORMAT)
            stop = stop.strftime(DATETIME_FORMAT)

            if waveform:
                return self.query_waveform(tag, start, stop, sampling_time=sampling_time)
            
            return self.query_trend(tag, start, stop, sampling_time=sampling_time)

        if values:

            period = self.get_period(tag)

            start = self.get_start(tag)
            stop = start + values * timedelta(seconds=period)

            start = start.strftime(DATETIME_FORMAT)
            stop = stop.strftime(DATETIME_FORMAT)

            if waveform:
                return self.query_waveform(tag, start, stop, sampling_time=sampling_time)
            
            return self.query_trend(tag, start, stop, sampling_time=sampling_time)
