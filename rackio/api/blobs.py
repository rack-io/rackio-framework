# -*- coding: utf-8 -*-
"""rackio/api/blobs.py

This module implements all class Resources for the Alarm Manager.
"""
import json
from io import BytesIO

from rackio import status_code

from .core import RackioResource

from ..dbmodels import Blob
 

class BlobResource(RackioResource):

    def on_get(self, req, resp, blob_name):

        pass

class BlobCollectionResource(RackioResource):

    def on_post(self, req, resp):
        
        blob_name = req.get_param('name')
        input_file = req.get_param('file')

        if not input_file.filename:
            resp.status = status_code.HTTP_BAD_REQUEST
        
        buf = BytesIO(input_file.file.read())

        Blob.create(name=blob_name, blob=buf.getvalue())

        resp.status = status_code.HTTP_201