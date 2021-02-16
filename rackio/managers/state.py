# -*- coding: utf-8 -*-
"""rackio/managers/state.py

This module implements Function Manager.
"""


class StateMachineManager:

    def __init__(self):

        self._machines = list()

    def append_machine(self, machine, interval=1, mode="sync"):
        
        self._machines.append((machine, interval, mode,))

    def get_machines(self):

        result = [_machine for _machine in self._machines]
        
        return result

    def get_machine(self, name):

        for _machine, interval, mode in self._machines:

            if name == _machine.name:

                return _machine

    def start_machine(self, name):

        for _machine, interval, mode in self._machines:

            if name == _machine.name:

                _machine.start()
                break

    def summary(self):

        result = dict()

        machines = [_machine.name for _machine, interval in self.get_machines()]

        result["length"] = len(machines)
        result["state_machines"] = machines

        return result
