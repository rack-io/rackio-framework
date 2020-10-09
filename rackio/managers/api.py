# -*- coding: utf-8 -*-
"""rackio/managers/api.py

Thi module implements API Manager.
"""

import falcon
from falcon_multipart.middleware import MultipartMiddleware

from ..api import TagResource, TagCollectionResource
from ..api import GroupResource, GroupCollectionResource
from ..api import TagHistoryResource, TrendResource, TrendCollectionResource
from ..api import LoggerResource
from ..api import ControlResource, ControlCollectionResource
from ..api import RuleResource, RuleCollectionResource
from ..api import AlarmResource, AlarmCollectionResource
from ..api import EventCollectionResource
from ..api import AppSummaryResource
from ..api import BlobCollectionResource, BlobResource

from ..web import StaticResource, resource_pairs


class APIManager:

    def __init__(self):

        self.app = falcon.API(middleware=[MultipartMiddleware()])

        self.port = 8000
        self.mode = "development"

        self.init_api()
        self.init_web()

    def set_mode(self, mode):

        self.mode = mode

    def set_port(self, port):

        self.port = port

    def init_api(self):

        _tag = TagResource()
        _tags = TagCollectionResource()
        _group = GroupResource()
        _groups = GroupCollectionResource()
        _tag_history = TagHistoryResource()
        _tag_trend = TrendResource()
        _tag_trends = TrendCollectionResource()
        _logger = LoggerResource()
        _control = ControlResource()
        _controls = ControlCollectionResource()
        _rule = RuleResource()
        _rules = RuleCollectionResource()
        _alarm = AlarmResource()
        _alarms = AlarmCollectionResource()
        _events = EventCollectionResource()
        _summary = AppSummaryResource()
        _blobs = BlobCollectionResource()
        _blob = BlobResource()

        self.app.add_route('/api/tags/{tag_id}', _tag)
        self.app.add_route('/api/tags', _tags)

        self.app.add_route('/api/groups/{group_id}', _group)
        self.app.add_route('/api/groups', _groups)

        self.app.add_route('/api/history/{tag_id}', _tag_history)
        self.app.add_route('/api/trends/{tag_id}', _tag_trend)
        self.app.add_route('/api/trends', _tag_trends)
        self.app.add_route('/api/logger', _logger)

        self.app.add_route('/api/controls/{control_name}', _control)
        self.app.add_route('/api/controls', _controls)

        self.app.add_route('/api/rules/{rule_name}', _rule)
        self.app.add_route('/api/rules', _rules)
        
        self.app.add_route('/api/alarms/{alarm_name}', _alarm)
        self.app.add_route('/api/alarms', _alarms)

        self.app.add_route('/api/events', _events)

        self.app.add_route('/api/summary', _summary)

        self.app.add_route('/api/blobs', _blobs)
        self.app.add_route('/api/blobs/{blob_name}', _blob)

    def init_web(self):

        web = self.app

        _static = StaticResource()

        pairs = resource_pairs()
        
        for path, route in pairs:

            route += "/{filename}"

            web.add_route(route, _static)

    def add_route(self, route, resource):

        self.app.add_route(route, resource)