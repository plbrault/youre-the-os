from engine.scene_object import SceneObject
from scene_objects.views.cpu_view import CpuView


class Cpu(SceneObject):
    def __init__(self, physical_id, logical_id, cpu_manager, *, process_happiness_ms, penalty_ms):
        self._physical_id = physical_id
        self._logical_id = logical_id
        self._cpu_manager = cpu_manager
        self._process_happiness_ms = process_happiness_ms
        self._penalty_ms = penalty_ms

        self._process = None

        super().__init__(CpuView(self))

    @property
    def physical_id(self):
        return self._physical_id

    @property
    def logical_id(self):
        return self._logical_id

    @property
    def process_happiness_ms(self):
        penalty_ms = self._penalty_ms if self._cpu_manager.check_cpu_for_penalty(self) else 0
        return self._process_happiness_ms + penalty_ms

    @property
    def has_process(self):
        return self._process is not None

    @property
    def process(self):
        return self._process

    @process.setter
    def process(self, process):
        self._process = process

    def update(self, current_time, events):
        pass
