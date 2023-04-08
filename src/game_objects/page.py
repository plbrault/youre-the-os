from lib.game_object import GameObject
from game_objects.views.page_view import PageView

class Page(GameObject):    
    def __init__(self):
        super().__init__(PageView(self))
        
    def update(self, current_time, events):
        pass
