from datetime import timedelta

from lib.game_object import GameObject
from game_objects.views.uptime_manager_view import UptimeManagerView

class UptimeManager(GameObject):
    
    def __init__(self, game):
        self._last_reset_time = 0
        self._uptime_text = '0:00:00'       
        super().__init__(UptimeManagerView(self))
            
    def reset(self):
        self._last_reset_time = self.game.current_time
       
    def update(self, current_time, events):
        uptime = current_time - self._last_reset_time
        if uptime % 1000 == 0:
            self._uptime_text = str(timedelta(milliseconds=uptime))
    