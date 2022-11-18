import pygame

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_10

class ProcessView(Drawable):
    def __init__(self, process):
        self._process = process
        super().__init__()

    @property
    def width(self):
        return 64

    @property
    def height(self):
        return 64

    def draw(self, surface):
        pygame.draw.rect(surface, Color.GREEN, pygame.Rect(self._x, self._y, self.width, self.height))
        text_surface = FONT_ARIAL_10.render(self._process.state, False, Color.BLACK)
        surface.blit(text_surface, (self._x + 18, self._y + 27))
