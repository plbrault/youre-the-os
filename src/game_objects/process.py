from fractions import Fraction
from random import randint

from lib.game_object import GameObject
from lib.game_event_type import GameEventType
from game_objects.process_state import ProcessState
from game_objects.views.process_view import ProcessView

class Process(GameObject):
    def __init__(self):
        self._state = ProcessState.NEW
        self._io_probability = randint(0, 50)
        self._ending_probability = randint(0, 5)
        self._total_cpu_time = 0
        self._total_idle_time = 0
        self._last_update_time = 0
        super().__init__(ProcessView(self))

    @property
    def state(self):
        return self._state

    @property
    def running_idle_ratio(self):
        return Fraction(self._total_cpu_time, self._total_idle_time).limit_denominator()

    def give_cpu_time(self):
        self._state = ProcessState.RUNNING

    def yield_cpu(self):
        if self._state == ProcessState.RUNNING:
            self._state = ProcessState.READY

    def _clickedOn(self, event):
        if event.type == GameEventType.MOUSE_LEFT_CLICK:
            return self._view.collides(*event.getProperty('position'))
        return False

    def update(self, current_time, events):
        for event in events:
            if self._clickedOn(event):
                self._state = ProcessState.RUNNING

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
