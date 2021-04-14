# -*- coding: utf-8 -*-
"""rackio/managers/api.py

Thi module implements API Manager.
"""

import falcon
from falcon import api_helpers as helpers
from falcon_auth import FalconAuthMiddleware, TokenAuthBackend
from falcon_multipart.middleware import MultipartMiddleware
from falcon_cors import CORS

from ..api import TagResource, TagCollectionResource
from ..api import GroupResource, GroupCollectionResource
from ..api import TagHistoryResource, TrendResource, TrendCollectionResource
from ..api import WaveformResource, WaveformCollectionResource
from ..api import LoggerResource
from ..api import ControlResource, ControlCollectionResource
from ..api import RuleResource, RuleCollectionResource
from ..api import AlarmResource, AlarmCollectionResource
from ..api import EventCollectionResource
from ..api import AppSummaryResource
from ..api import BlobCollectionResource, BlobResource
from ..api import UserCollectionResource, UsercolumnsCollectionResource, UserColumnResource
from ..api import UserLicenseResource
from ..api import LicenseResource

from ..api import LoginResource, LogoutResource

from ..web import StaticResource, resource_pairs

from ..dao import AuthDAO

def user_loader(token):

    dao = AuthDAO()

    user = dao.read_by_key(token)

    if not user:
        return None

    username = user.username

    return {'username': username}


class API(falcon.API):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.multipart_middleware = MultipartMiddleware()

        self.auth_backend = TokenAuthBackend(user_loader, auth_header_prefix='Token')
        
        self.auth_middleware = FalconAuthMiddleware(self.auth_backend,
            exempt_routes=['/api/login'], exempt_methods=['HEAD'])

        self.auth = False
        self.cors_origins = list()

    def set_auth(self, enabled=False):

        self.auth = enabled

    def auth_enabled(self):

        return self.auth

    def set_cors(self, allow_origins):

        self.cors_origins = allow_origins

    def get_cors(self):

        return self.cors_origins

    def set_middleware(self, independent_middleware=True):
        
        middleware = [self.multipart_middleware]

        if self.auth:
            middleware.append(self.auth_middleware)
        
        if self.cors_origins:
            cors = CORS(allow_origins_list=self.cors_origins)
            middleware.append(cors.middleware)

        self._middleware = helpers.prepare_middleware(
            middleware, independent_middleware=independent_middleware)
        self._independent_middleware = independent_middleware        


class APIManager:

    def __init__(self):

        self.app = API()

        self.port = 8000
        self.mode = "development"

        self.init_api()
        self.init_web()

    def set_mode(self, mode):

        self.mode = mode

    def enable_auth(self):

        self.app.set_auth(True)

    def disable_auth(self):

        self.app.set_auth(False)

    def auth_enabled(self):

        return self.app.auth_enabled()

    def set_cors(self, allow_origins):

        self.app.set_cors(allow_origins)

    def get_cors(self):

        return self.app.get_cors()

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
        _tag_waveform = WaveformResource()
        _tag_waveforms = WaveformCollectionResource()
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
        _login = LoginResource()
        _logout = LogoutResource()
        _users = UserCollectionResource()
        _users_columns = UsercolumnsCollectionResource()
        _users_column = UserColumnResource()
        _users_license = UserLicenseResource()
        _license = LicenseResource()

        self.app.add_route('/api/tags/{tag_id}', _tag)
        self.app.add_route('/api/tags', _tags)

        self.app.add_route('/api/groups/{group_id}', _group)
        self.app.add_route('/api/groups', _groups)

        self.app.add_route('/api/history/{tag_id}', _tag_history)
        self.app.add_route('/api/trends/{tag_id}', _tag_trend)
        self.app.add_route('/api/trends', _tag_trends)
        self.app.add_route('/api/waveforms/{tag_id}', _tag_waveform)
        self.app.add_route('/api/waveforms', _tag_waveforms)
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

        self.app.add_route('/api/login', _login)
        self.app.add_route('/api/logout', _logout)

        self.app.add_route('/api/users', _users)
        self.app.add_route('/api/users/columns', _users_columns)
        self.app.add_route('/api/users/columns/{column_name}', _users_column)
        self.app.add_route('/api/users/license', _users_license)

        self.app.add_route('/api/license', _license)

    def init_web(self):

        web = self.app

        _static = StaticResource()

        pairs = resource_pairs()
        
        for path, route in pairs:

            route += "/{filename}"

            web.add_route(route, _static)

    def add_route(self, route, resource):

        self.app.add_route(route, resource)
         