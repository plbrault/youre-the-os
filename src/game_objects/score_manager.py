from lib.game_object import GameObject
from game_objects.views.score_manager_view import ScoreManagerView

class ScoreManager(GameObject):
    
    def __init__(self, game):
        self._process_manager = game.process_manager
        super().__init__(ScoreManagerView(self))
        
    def update(self, current_time, events):
        if current_time % 1000 == 0:
            print(self._process_manager.get_current_stats())
    