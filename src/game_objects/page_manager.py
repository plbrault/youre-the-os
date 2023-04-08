from lib.ui.fonts import FONT_ARIAL_20
from lib.game_object import GameObject
from game_objects.label import Label
from game_objects.views.page_manager_view import PageManagerView
from game_objects.page import Page
from game_objects.page_slot import PageSlot

class PageManager(GameObject):
    _MAX_PAGES= 168
    
    def __init__(self, game, ram_size):
        self._game = game
        self._ram_size = ram_size
        
        self._ram_slots = []
        
        super().__init__(PageManagerView(self))
        
        self._setup()
        
    def _setup(self):
        ram_pages_label = Label('RAM Pages :')
        ram_pages_label.view.set_xy(self._game.process_manager.view.width, 120)
        ram_pages_label.font = FONT_ARIAL_20
        self.children.append(ram_pages_label)
        
        for row in range(14):
            for column in range(12):
                ram_slot = PageSlot()          
                x = self._game.process_manager.view.width + column * ram_slot.view.width + column * 5
                y = 150 + row * ram_slot.view.height + row * 5
                ram_slot.view.set_xy(x, y)
                self._ram_slots.append(ram_slot)
        self.children.extend(self._ram_slots)
        
    def create_page(self):
        page = Page()
        for ram_slot in self._ram_slots:
            if not ram_slot.has_page:
                ram_slot.page = page
                page.view.set_xy(ram_slot.view.x, ram_slot.view.y)
                break
        self.children.append(page)
        return page
        
    def update(self, current_time, events):
        pass
