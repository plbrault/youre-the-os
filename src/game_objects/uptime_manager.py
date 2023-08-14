from datetime import timedelta

from lib.game_object import GameObject
from game_objects.views.uptime_manager_view import UptimeManagerView

class UptimeManager(GameObject):
    
    def __init__(self, game, current_time):
        self._game = game
        
        self._last_update_time = current_time
        self._uptime = 0
        self._uptime_text = '0:00:00'
        
        self._is_paused = False 
        self._paused_time = 0
          
        super().__init__(UptimeManagerView(self))
    
    @property
    def uptime_text(self):
        return self._uptime_text
    
    def pause(self):
        self._is_paused = True
        self._paused_time = self._game.current_time
        
    def resume(self):
        self._is_paused = False
        self._last_update_time = self._game.current_time - (self._paused_time - self._last_update_time)
       
    def update(self, current_time, events):
        if not self._is_paused:
            if current_time - self._last_update_time >= 1000:
                self._last_update_time = current_time
                self._uptime += 1000
            self._uptime_text = str(timedelta(seconds=int(self._uptime / 1000)))
    