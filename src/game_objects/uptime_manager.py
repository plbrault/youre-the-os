from datetime import timedelta

from lib.constants import ONE_SECOND
from lib.game_object import GameObject
from game_objects.views.uptime_manager_view import UptimeManagerView


class UptimeManager(GameObject):

    def __init__(self, game):
        self._game = game

        self._last_update_time = game.current_time
        self._uptime = 0
        self._uptime_text = '0:00:00'

        super().__init__(UptimeManagerView(self))

    @property
    def uptime_text(self):
        return self._uptime_text

    def update(self, current_time, events):
        if current_time - self._last_update_time >= ONE_SECOND:
            self._last_update_time = current_time
            self._uptime += ONE_SECOND
        self._uptime_text = str(timedelta(seconds=int(self._uptime / ONE_SECOND)))
