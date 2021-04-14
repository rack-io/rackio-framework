# -*- coding: utf-8 -*-
"""rackio/dao/licenses.py

This module implements Licenses Data Objects Access.
"""
from .core import RackioDAO

from ..dbmodels import License
from ..utils import serialize_dbo, hash_license



class LicensesDAO(RackioDAO):


    def add(self, lic):
        r"""
        Documentation here
        """
        License.add(lic)
        result = {
            'message': 200
        }
        return result
