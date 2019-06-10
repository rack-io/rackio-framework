# -*- coding: utf-8 -*-
"""CVT/tests.py

This module implements a base utility classes and utility functions.
"""

import concurrent.futures

from .engine import CVTEngine

def writer(cvt):

    cvt.request({
        "action": "set_value",
        "parameters": {
            "name": "T01",
            "value": 24,
        }
    })
    
    response = cvt.response()
    print("writer ", response)

def reader(cvt):

    cvt.request({
        "action": "get_value",
        "parameters": {
            "name": "T01",
        }
    })
    
    response = cvt.response()
    print("reader ", response)

    engine = CVTEngine()

    engine.request({
        "action": "get_value",
        "parameters": {
            "name": "T01",
        }
    })
    response = engine.response()
    print("reader ", response)


if __name__ == "__main__":

    engine = CVTEngine()

    engine.set_tag("T01", "int")
    engine.set_tag("P01", "int")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

        executor.submit(writer, engine)
        executor.submit(reader, engine)        
        