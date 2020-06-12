# -*- coding: utf-8 -*-
"""rackio/utils.py

This module implements a base utility classes and utility functions.
"""

import os

from datetime import datetime, timedelta
from rackio import status_code
import abc

class Observer(metaclass=abc.ABCMeta):
    """
    Define an updating interface for objects that should be notified of
    changes in a subject.
    """

    def __init__(self):
        self._subject = None
        self._observer_state = None

    @abc.abstractmethod
    def update(self, arg):
        pass


def serialize_dbo(dbo):

    result = dict()

    data = dbo.__dict__["__data__"]
    
    for key, value in data.items():

        if isinstance(value, datetime):

            result[key] = value.strftime('%Y-%m-%d %H:%M:%S')

        else:
            
            result[key] = value
    
    return result

def process_waveform(waveform, tstart, tstop):

    start_date = datetime.strptime(tstart, '%Y-%m-%d %H:%M:%S')
    finish_date = datetime.strptime(tstop, '%Y-%m-%d %H:%M:%S')
    
    dt = waveform["dt"]
    values = waveform["values"][:]
    t0 = waveform["t0"]

    first_date = datetime.strptime(t0, '%Y-%m-%d %H:%M:%S')
    time_delta = timedelta(seconds=dt)

    result = list()
    result_waveform = dict()

    result_waveform["dt"] = dt

    while first_date < start_date:

        values.pop(0)
        first_date += time_delta
    
    result_waveform["t0"] = first_date.strftime('%Y-%m-%d %H:%M:%S')

    while first_date < finish_date:

        if len(values) > 0:
            value = values.pop(0)
            result.append(value)
            
            first_date += time_delta
        else:
            finish_date = first_date
            break

    result_waveform["values"] = result

    return result_waveform

def framework_path():

    return os.path.dirname(status_code.__file__)

def directory_path(directory):

    return os.path.join(framework_path(), directory)

def directory_files(path):

    files = os.listdir(path)
    all_files = list()
    
    for entry in files:
        
        full_path = os.path.join(path, entry)
        
        if os.path.isdir(full_path):
            all_files += directory_files(full_path)
        else:
            all_files.append(full_path)
                
    return all_files

def directory_paths(directory):

    path = directory_path(directory)
    files = directory_files(path)

    preresult = list()

    for path in files:

        preresult.append(os.path.split(path)[0])

    preresult = list(set(preresult))

    result = list()

    for path in preresult:
        result.append(path.split(directory)[-1])

    return result
