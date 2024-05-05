from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_PRIMARY_LARGE
from window_size import WINDOW_HEIGHT


class PageManagerView(Drawable):
    def __init__(self, page_manager):
        self._page_manager = page_manager
        super().__init__()

        self._pages_in_ram_text_surface = FONT_PRIMARY_LARGE.render(
            'Memory Pages in RAM :', False, Color.WHITE)
        self._pages_in_swap_space_text_surface = FONT_PRIMARY_LARGE.render(
            'Memory Pages on Disk :', False, Color.WHITE)

    @property
    def width(self):
        return 691

    @property
    def height(self):
        return WINDOW_HEIGHT

    def draw(self, surface):
        surface.blit(self._pages_in_ram_text_surface,
                     self._page_manager.pages_in_ram_label_xy)
        if self._page_manager.pages_in_swap_label_xy is not None:
            surface.blit(self._pages_in_swap_space_text_surface,
                         self._page_manager.pages_in_swap_label_xy)
