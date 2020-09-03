# -*- coding: utf-8 -*-
"""rackio/workers/state.py

This module implements State Machine Worker.
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler


class StateMachineWorker():

    def __init__(self, manager):
        
        self._manager = manager
        self._scheduler = BackgroundScheduler()
        logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)

        self.jobs = list()

    def loop_closure(self, machine):

        def loop():

            machine.loop()

        return loop

    def start(self):

        for machine, interval in self._manager.get_machines():
            
            loop = self.loop_closure(machine)
            job = self._scheduler.add_job(loop, 'interval', seconds=interval)

            self.jobs.append(job)
        
        self._scheduler.start()
    