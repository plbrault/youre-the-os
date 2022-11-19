from fractions import Fraction
from random import randint

from lib.game_object import GameObject
from lib.game_event_type import GameEventType
from game_objects.process_state import ProcessState
from game_objects.views.process_view import ProcessView

class Process(GameObject):
    def __init__(self, cpu_list, process_slots):
        self._cpu_list = cpu_list
        self._process_slots = process_slots

        self._state = ProcessState.NEW
        self._io_probability = randint(0, 50)
        self._ending_probability = randint(0, 5)
        self._total_cpu_time = 0
        self._total_idle_time = 0
        self._last_update_time = 0
        self._current_cpu = None

        super().__init__(ProcessView(self))

    @property
    def state(self):
        return self._state

    @property
    def total_cpu_time(self):
        return self._total_cpu_time

    @property
    def total_idle_time(self):
        return self._total_idle_time

    def _use_cpu(self):
        if self._current_cpu is None:
            for cpu in self._cpu_list:
                if not cpu.has_process:
                    cpu.process = self
                    self._current_cpu = cpu
                    self._view.setXY(cpu.view.x, cpu.view.y)
                    if self._state == ProcessState.NEW or ProcessState.READY:
                        self._state = ProcessState.RUNNING
                    break
            if self._current_cpu is not None:
                for slot in self._process_slots:
                    if slot.process == self:
                        slot.process = None
                        break

    def _yield_cpu(self):
        if self._current_cpu is not None:
            if self._state == ProcessState.RUNNING:
                self._state = ProcessState.READY
            self._current_cpu.process = None
            self._current_cpu = None
            for slot in self._process_slots:
                if slot.process is None:
                    slot.process = self
                    self._view.setXY(slot.view.x, slot.view.y)
                    break

    def _checkIfClickedOn(self, event):
        if event.type == GameEventType.MOUSE_LEFT_CLICK:
            return self._view.collides(*event.getProperty('position'))
        return False

    def _onClick(self):
        if self._current_cpu is not None:
            self._yield_cpu()
        else:
            self._use_cpu()

    def update(self, current_time, events):
        for event in events:
            if self._checkIfClickedOn(event):
                self._onClick()

        if current_time >= self._last_update_time + 1000:
            self._last_update_time = current_time
            if self._state != ProcessState.RUNNING and self._state != ProcessState.ENDED:
                self._total_idle_time += 1
            elif self._state == ProcessState.RUNNING:
                self._total_cpu_time += 1
                #if (randint(0, 100) <= self._io_probability):
                #    self._state = ProcessState.WAITING_IO
                #elif (randint(0, 100) <= self._ending_probability):
                #    self._state = ProcessState.ENDED
