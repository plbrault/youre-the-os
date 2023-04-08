from lib.ui.fonts import FONT_ARIAL_20
from lib.game_object import GameObject
from game_objects.label import Label
from game_objects.views.page_manager_view import PageManagerView

class PageManager(GameObject):
    _MAX_PAGES= 156
    
    def __init__(self, game, ram_size):
        self._game = game
        self._ram_size = ram_size
        super().__init__(PageManagerView(self))
        
        self._setup()
        
    def _setup(self):
        ram_pages_label = Label('RAM Pages :')
        ram_pages_label.view.set_xy(self._game.process_manager.view.width, 120)
        ram_pages_label.font = FONT_ARIAL_20
        self.children.append(ram_pages_label)
        
    def update(self, current_time, events):
        pass
