# -*- coding: utf-8 -*-
"""rackio/workers/state.py

This module implements State Machine Worker.
"""
import heapq
import logging
import time

from collections import deque

from apscheduler.schedulers.background import BackgroundScheduler

from .worker import BaseWorker


class MachineSched():

    def __init__(self):

        self._ready = deque()
        self._sleeping = list()
        self._sequence = 0
        self._stop = False

    def call_soon(self, func):
        
        self._ready.append(func)

    def call_later(self, delay, func):
        
        self._sequence += 1
        deadline = time.time() + delay
        heapq.heappush(self._sleeping, (deadline, self._sequence, func))

    def stop(self):

        self._stop = True
    
    def run(self):
        while self._ready or self._sleeping:

            if self._stop:
                break

            if not self._ready:
                deadline, _, func = heapq.heappop(self._sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self._ready.append(func)

            while self._ready:
                
                func = self._ready.popleft()
                func()



class StateMachineWorker(BaseWorker):

    def __init__(self, manager):

        super(StateMachineWorker, self).__init__()
        
        self._manager = manager
        self._scheduler = MachineSched()

        self.jobs = list()

    def loop_closure(self, machine, interval):

        def loop():
            machine.loop()
            self._scheduler.call_later(interval, loop)

        return loop

    def run(self):

        for machine, interval in self._manager.get_machines():
            func = self.loop_closure(machine, interval)
            self._scheduler.call_soon(func)

        self._scheduler.run()

    def stop(self):

        self._scheduler.stop()
    