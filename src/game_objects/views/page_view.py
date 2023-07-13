import pygame

from lib.ui.color import Color
from lib.drawable import Drawable
from lib.ui.fonts import FONT_ARIAL_8

class PageView(Drawable):
    def __init__(self, page):
        self._page = page
        self._pid_text_surface = FONT_ARIAL_8.render('PID ' + str(self._page.pid), False, Color.BLACK)
        super().__init__()
        
    @property
    def width(self):
        return 32

    @property
    def height(self):
        return 32
    
    def draw(self, surface):
        color = Color.DARK_GREY
        if self._page.display_blink_color:
            color = Color.BLUE
        elif self._page.in_use:
            color = Color.WHITE
        pygame.draw.rect(surface, color, pygame.Rect(self._x, self._y, self.width, self.height))
        surface.blit(self._pid_text_surface, (self._x + 5, self._y + 5))
        