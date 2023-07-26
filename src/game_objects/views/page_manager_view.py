from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_24

class PageManagerView(Drawable):
    def __init__(self, page_manager):
        self.page_manager = page_manager
        super().__init__()
        
        self._pages_in_ram_text_surface = FONT_PRIMARY_24.render('Memory Pages in RAM :', False, Color.WHITE)
        self._pages_in_swap_space_text_surface = FONT_PRIMARY_24.render('Memory Pages on Disk :', False, Color.WHITE)        

    @property
    def width(self):
        return 494

    @property
    def height(self):
        return 768

    def draw(self, surface):
        surface.blit(self._pages_in_ram_text_surface, self.page_manager.pages_in_ram_label_xy)
        surface.blit(self._pages_in_swap_space_text_surface, self.page_manager.pages_in_swap_label_xy)
