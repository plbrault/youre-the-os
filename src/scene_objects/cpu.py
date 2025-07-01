from engine.scene_object import SceneObject
from scene_objects.views.cpu_view import CpuView


class Cpu(SceneObject):
    def __init__(self, id, *, _time_for_process_happiness=5000):
        self._id = id
        self._process = None

        self._time_for_process_happiness = _time_for_process_happiness

        super().__init__(CpuView(self))

    @property
    def id(self):
        return self._id

    @property
    def time_for_process_happiness(self):
        return self._time_for_process_happiness

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
