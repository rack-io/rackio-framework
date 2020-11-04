# -*- coding: utf-8 -*-

import os
import mimetypes

external_mimetypes = {
    ".ttf": "font/ttf",
    ".woff": "font/woff",
    ".woff2": "font/woff2" 
}

def get_extension(filename):

    filename, file_extension = os.path.splitext(filename)

    return file_extension

def get_content_type(filename):

    ext = get_extension(filename)

    if ext in (".ttf", ".woff", ".woff2"):
        return external_mimetypes[ext]

    return mimetypes.types_map[ext]

def uri_to_path(uri):

    return uri.split("/")[:-1]

def get_static_path(stack, filename):

    path = os.getcwd()

    for name in stack:
        path = os.path.join(path, name)

    path = os.path.join(path, filename)

    return path

def traverse_static():

    directory = os.getcwd()

    path = os.path.join(directory, "static")

    return [x[0] for x in os.walk(path)]

def resource_pairs():

    directory = os.getcwd()
    paths = traverse_static()

    result = list()
    
    for path in paths:

        short = path.replace(directory, "")
        record = (short, short.replace(os.sep, "/"))

        result.append(record)

    return result