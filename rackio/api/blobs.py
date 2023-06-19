# -*- coding: utf-8 -*-
"""rackio/api/blobs.py

This module implements all class Resources for the Alarm Manager.
"""
import json
from io import BytesIO

from rackio import status_code

from .core import RackioResource
from .auth_hook import authorize

from ..dbmodels import Blob
from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, VISITOR_ROLE


class BlobResource(RackioResource):
    @authorize([SYSTEM_ROLE, ADMIN_ROLE])
    def on_get(self, req, resp, blob_name):
        resp.status = status_code.HTTP_200
        resp.content_type = "application/octet-stream"
        resp.downloadable_as = "{}.pkl".format(blob_name)

        resp.body = Blob.get_value(blob_name)


class BlobCollectionResource(RackioResource):
    @authorize([SYSTEM_ROLE, ADMIN_ROLE])
    def on_post(self, req, resp):
        blob_name = req.get_param("name")
        input_file = req.get_param("file")

        if not input_file.filename:
            resp.status = status_code.HTTP_BAD_REQUEST

        buf = BytesIO(input_file.file.read())

        Blob.create(name=blob_name, blob=buf.getvalue())

        resp.status = status_code.HTTP_201
