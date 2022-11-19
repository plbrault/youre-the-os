from lib.game_object import GameObject
from lib.game_event_type import GameEventType
from game_objects.views.process_view import ProcessView

class Process(GameObject):
    def __init__(self, pid, cpu_list, process_slots):
        self._pid = pid
        self._cpu_list = cpu_list
        self._process_slots = process_slots

        self._has_cpu = False
        self._is_blocked = False
        self._has_ended = False
        self._time_since_state_change = 0

        self._last_update_time = 0

        super().__init__(ProcessView(self))

    @property
    def pid(self):
        return self._pid

    @property
    def has_cpu(self):
        return self._has_cpu

    @property
    def is_blocked(self):
        return self._is_blocked

    @property
    def has_ended(self):
        return self._has_ended

    @property
    def time_since_state_change(self):
        return self._time_since_state_change

    def _use_cpu(self):
        if not self.has_cpu:
            for cpu in self._cpu_list:
                if not cpu.has_process:
                    cpu.process = self
                    self._has_cpu = True
                    self._view.setXY(cpu.view.x, cpu.view.y)
                    break
            if self.has_cpu:
                self._time_since_state_change = 0
                for slot in self._process_slots:
                    if slot.process == self:
                        slot.process = None
                        break

    def _yield_cpu(self):
        if self.has_cpu:
            self._has_cpu = False
            self._time_since_state_change = 0
            for cpu in self._cpu_list:
                if cpu.process == self:
                    cpu.process = None
                    break
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
        if self.has_cpu:
            self._yield_cpu()
        else:
            self._use_cpu()

    def update(self, current_time, events):
        for event in events:
            if self._checkIfClickedOn(event):
                self._onClick()

        if current_time >= self._last_update_time + 1000:
            self._time_since_state_change += 1
