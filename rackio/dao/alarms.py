# -*- coding: utf-8 -*-
"""rackio/dao/alarms.py

This module implements Alarms Data Objects Access.
"""
from .core import RackioDAO

from datetime import datetime


class AlarmsDAO(RackioDAO):
    def get_all_active(self):
        r"""
        Documentation here
        """
        app = self.get_app()
        manager = app.get_manager("alarm")

        result = list()

        for alarm in manager.get_alarms():
            _alarm = alarm.serialize()

            if _alarm["triggered"]:
                result.append(_alarm)

        if len(result) > 0:
            result.sort(reverse=True, key=self.sort)

        return result

    def get_all(self):
        app = self.get_app()
        manager = app.get_manager("alarm")

        result = list()

        for alarm in manager.get_alarms():
            result.append(alarm.serialize())

        return result

    def get(self, name, serialize=True):
        app = self.get_app()
        manager = app.get_manager("alarm")

        alarm = manager.get_alarm(name)

        if not alarm:
            return

        if serialize:
            return alarm.serialize()

        return alarm

    def update(self, name, action):
        alarm = self.get(name, serialize=False)

        if not alarm:
            return

        if action == "Acknowledge":
            alarm.acknowledge()

        elif action == "Enable":
            alarm.enable()

        elif action == "Disable":
            alarm.disable()

        elif action == "Reset":
            alarm.to_reset()

        elif action == "Confirm reset":
            alarm.reset()

        elif action == "Silence":
            alarm.silence()

        elif action == "Sound":
            alarm.sound()

        elif action == "Shelve":
            alarm.shelve()

        elif action == "Unshelve":
            alarm.unshelve()

        elif action == "Supress by design":
            alarm.supress_by_design()

        elif action == "Unsupress by design":
            alarm.unsupress_by_design()

        elif action == "Out of service":
            alarm.out_of_service()

        elif action == "In service":
            alarm.in_service()

        return alarm.serialize()

    @staticmethod
    def sort(e):
        r"""
        Documentation here
        """
        return datetime.strptime(e["tripped_timestamp"], "%Y-%m-%d %H:%M:%S")
