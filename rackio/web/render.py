# -*- coding: utf-8 -*-

import os

from jinja2 import Template

def render_template(template, **kwargs):

    dirs = ["templates"] + template.split("/")
    path = os.path.join(*tuple(dirs))
    
    with open(path, 'r', encoding='utf8', errors='ignore') as f:
        content = f.read()
    
    t = Template(content)

    return t.render(**kwargs)


def raw_template(template, **kwargs):

    dirs = ["templates"] + template.split("/")
    path = os.path.join(*tuple(dirs))
    
    with open(path, 'r', encoding='utf8', errors='ignore') as f:
        content = f.read()

    return content