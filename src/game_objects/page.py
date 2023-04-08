from lib.game_object import GameObject
from game_objects.views.page_view import PageView

class Page(GameObject):    
    def __init__(self):
        self._in_use = False
        
        super().__init__(PageView(self))
        
    @property
    def in_use(self):     
        return self._in_use
    
    @in_use.setter
    def in_use(self, value):
        self._in_use = value
        
    def update(self, current_time, events):
        pass
