import pygame

from lib.ui.color import Color
from lib.drawable import Drawable

class PageView(Drawable):
    def __init__(self, page):
        self._page = page
        super().__init__()
        
    @property
    def width(self):
        return 32

    @property
    def height(self):
        return 32
    
    def draw(self, surface):
        pygame.draw.rect(surface, Color.DARK_GREY, pygame.Rect(self._x, self._y, self.width, self.height))
        