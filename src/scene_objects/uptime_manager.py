from datetime import timedelta

from constants import ONE_SECOND
from engine.scene_object import SceneObject
from scene_objects.views.uptime_manager_view import UptimeManagerView


class UptimeManager(SceneObject):

    def __init__(self, stage):
        self._stage = stage

        self._last_update_time = stage.current_time
        self._uptime = 0
        self._uptime_text = '0:00:00'

        super().__init__(UptimeManagerView(self))

    @property
    def uptime_ms(self):
        return self._uptime

    @property
    def uptime_text(self):
        return self._uptime_text

    def update(self, current_time, events):
        if current_time - self._last_update_time >= ONE_SECOND:
            self._last_update_time = current_time
            self._uptime += ONE_SECOND
        self._uptime_text = str(timedelta(seconds=int(self._uptime / ONE_SECOND)))
