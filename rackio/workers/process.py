# -*- coding: utf-8 -*-
"""rackio/workers/process.py

This module implements all thread classes for process workers.
"""

from multiprocessing import Process

from ..engine import CVTEngine


class ProcessWorker(Process):

    def __init__(self):

        super(ProcessWorker, self).__init__()

        self.tag_engine = CVTEngine()