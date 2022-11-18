from lib.game_object import GameObject
from game_objects.views.cpu_view import CpuView

class Cpu(GameObject):
    def __init__(self, cpu_id):
        self._cpu_id = cpu_id

        super().__init__(CpuView(self))

    @property
    def cpu_id(self):
        return self._cpu_id

    def update(self, current_time):
        pass
    