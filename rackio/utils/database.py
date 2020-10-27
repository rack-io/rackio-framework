# -*- coding: utf-8 -*-
"""rackio/utils/database.py

This module implements Database Utility Functions.
"""
from datetime import datetime, date

def serialize_dbo(dbo):

    result = dict()

    data = dbo.__dict__["__data__"]
    
    for key, value in data.items():

        if isinstance(value, datetime):

            result[key] = value.strftime('%Y-%m-%d %H:%M:%S')

        elif isinstance(value, date):

            result[key] = value.strftime('%Y-%m-%d')

        else:
            
            result[key] = value
    
    return result