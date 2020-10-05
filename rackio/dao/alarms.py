# -*- coding: utf-8 -*-
"""rackio/dao/alarms.py

This module implements Alarms Data Objects Access.
"""
from .core import RackioDAO


class AlarmDAO(RackioDAO):

    def get_all(self):

        app = self.get_app()
        manager = app.get_manager("alarm")

        result = list()

        for alarm in manager.get_alarms():

            result.append(alarm.serialize())

        return result

    def get(self, name):

        app = self.get_app()
        manager = app.get_manager("alarm")

        alarm = manager.get_alarm(name)

        if alarm:
            return alarm.serialize()

    def update(self, name, action):

        alarm = self.get(name)

        if not alarm:
            return

        if action == "Acknowledge":
    
            alarm.acknowledge()
        
        elif action == "Enable":

            alarm.enable()

        elif action == "Disable":

            alarm.disable()

        elif action == "Reset":

            alarm.reset()

        return alarm.serialize()
