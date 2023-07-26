from math import floor

from lib.game_object import GameObject
from game_objects.views.score_manager_view import ScoreManagerView

_UPDATE_INTERVAL = 100

class ScoreManager(GameObject):
    
    def __init__(self, game):
        self._process_manager = game.process_manager
        
        self._score = 0
        self._last_update_time = 0
        self._gracefully_terminated_process_count = 0
        self._user_terminated_process_count = 0
        
        super().__init__(ScoreManagerView(self))
        
    @property
    def score(self):
        return int(self._score)
        
    def update(self, current_time, events):
        if current_time - self._last_update_time >= _UPDATE_INTERVAL:
            self._last_update_time = current_time
            stats = self._process_manager.get_current_stats()
            for starvation_level in range(0, 6):
                """
                Points per second for each starvation level:
                0 -> 100
                1 -> 50
                2 -> 25
                3 -> 10
                4 -> 5
                5 -> 1
                """
                points_per_second = max(5 * floor(100 / 2 ** starvation_level / 5), 1)
                points = points_per_second / _UPDATE_INTERVAL
                self._score += points * stats['alive_process_count_by_starvation_level'][starvation_level]
            if stats['user_terminated_process_count'] != self._user_terminated_process_count:
                self._user_terminated_process_count = stats['user_terminated_process_count']
                self._score = max(0, self._score - 1000)
            if stats['gracefully_terminated_process_count'] != self._gracefully_terminated_process_count:
                self._gracefully_terminated_process_count = stats['gracefully_terminated_process_count']
                self._score += 200
    