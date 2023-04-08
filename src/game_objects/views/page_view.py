import pygame

from lib.ui.color import Color
from lib.drawable import Drawable

class PageView(Drawable):
    def __init__(self, page):
        self._page = page
        super().__init__()
        
    @property
    def width(self):
        return 16

    @property
    def height(self):
        return 16
    
    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self._x, self._y, self.width, self.height))
        