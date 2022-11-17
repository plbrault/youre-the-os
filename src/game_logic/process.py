from fractions import Fraction
from random import randint

from game_logic.process_state import ProcessState

class Process:
    def __init__(self):
        self._state = ProcessState.NEW
        self._io_probability = randint(0, 50)
        self._ending_probability = randint(0, 5)
        self._total_cpu_time = 0
        self._total_idle_time = 0
        self._last_update_time = 0

    def get_state(self):
        return self._state

    state = property(get_state)

    def get_running_idle_ratio(self):
        return Fraction(self._total_cpu_time, self._total_idle_time).limit_denominator()

    running_idle_ratio = property(get_running_idle_ratio)

    def give_cpu_time(self):
        self._state = ProcessState.RUNNING
        self._time_waiting = 0

    def yield_cpu(self):
        if self._state == ProcessState.RUNNING:
            self._state = ProcessState.READY

    def update(self, current_time):
        if current_time >= self._last_update_time + 1000:
            self._last_update_time = current_time
            if self._state != ProcessState.RUNNING and self._state != ProcessState.ENDED:
                self._total_idle_time += 1
            elif self._state == ProcessState.RUNNING:
                self._total_cpu_time += 1
                if (randint(0, 100) <= self._io_probability):
                    self._state = ProcessState.WAITING_IO
                elif (randint(0, 100) <= self._ending_probability):
                    self._state = ProcessState.ENDED
