# -*- coding: utf-8 -*-
"""rackio/state.py

This module implements all state machine classes.
"""

from statemachine import StateMachine, State


class StateMachineManager:

    def __init__(self):

        self._machines = list()

    def append_machine(self, machine):
        
        self._machines.append(machine)

    def get_machine(self, name):

        for machine in self._machines:

            if machine.name == name:

                return machine

