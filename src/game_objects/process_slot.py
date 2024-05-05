from engine.game_object import GameObject
from game_objects.views.process_slot_view import ProcessSlotView


class ProcessSlot(GameObject):
    def __init__(self):
        self._process = None

        super().__init__(ProcessSlotView())

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
