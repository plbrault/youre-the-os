from game_logic.process_state import ProcessState
from random import random

class Process:

    def __init__(self):
        self._state = ProcessState.READY
        self._time_waiting = 0
        self._io_probability = random() / 2

    def give_cpu_time(self):
        self._state = ProcessState.RUNNING
        self._time_waiting = 0

    def yield_cpu(self):
        if self._state == ProcessState.RUNNING:
            self._state = ProcessState.READY

    def update(self):
        if self._state == ProcessState.READY:
            self._time_waiting += 1
        if self._state == ProcessState.RUNNING:
          if (random() < self._io_probability):
            self._state = ProcessState.WAITING_IO
