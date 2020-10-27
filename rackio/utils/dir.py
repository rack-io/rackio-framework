# -*- coding: utf-8 -*-
"""rackio/utils/dir.py

This module implements Directory Utility Functions.
"""

import os

from rackio import status_code

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