# -*- coding: utf-8 -*-
"""rackio/utils/auth.py

This module implements Authentication Utility Functions.
"""

from uuid import uuid1
from hashlib import md5

def generate_key():

    return str(uuid1())

def hash_password(password):

    _hash = md5(password.encode())

    return _hash.hexdigest()

def verify_password(_hash, password):

    return _hash == hash_password(password)

def hash_license(lic):

    _hash = md5(lic.encode())

    return _hash.hexdigest()

def verify_license(_hash, lic):

    return _hash == hash_license(lic)