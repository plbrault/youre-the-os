from game_logic.process_state import ProcessState
from random import random

class Process:

    def __init__(self):
        self._state = ProcessState.READY
        self._io_probability = random() / 2
        self._total_cpu_time = 0
        self._total_idle_time = 0
        self._current_cpu_time = 0
        self._current_idle_time = 0

    def give_cpu_time(self):
        self._state = ProcessState.RUNNING
        self._time_waiting = 0

    def yield_cpu(self):
        if self._state == ProcessState.RUNNING:
            self._state = ProcessState.READY

    def update(self):
        if self._state == ProcessState.NEW or self._state == ProcessState.READY or self._state == ProcessState.WAITING_IO:
            self._total_idle_time += 1
            self._current_idle_time += 1
            self._current_cpu_time = 0
        if self._state == ProcessState.RUNNING:
          self._current_idle_time = 0
          self._total_cpu_time += 1
          self._current_cpu_time += 1
          if (random() < self._io_probability):
            self._state = ProcessState.WAITING_IO
