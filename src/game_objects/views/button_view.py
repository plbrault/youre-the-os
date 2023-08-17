import pygame

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_LARGE

class ButtonView(Drawable):
    def __init__(self, button):
        self._button = button
        super().__init__()

        self._min_width = 0
        self._text_surface = FONT_PRIMARY_LARGE.render(self._button.text.upper(), False, Color.WHITE)

    @property
    def min_width(self):
        return self._min_width

    @min_width.setter
    def min_width(self, value):
        self._min_width = value

    @property
    def width(self):
        return max(self.min_width, self._text_surface.get_width() + 24)

    @property
    def height(self):
        return self._text_surface.get_height() + 24

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self.x, self.y, self.width, self.height), border_radius=3)
        pygame.draw.rect(surface, Color.ALMOST_BLACK, pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4), border_radius=3)
        surface.blit(self._text_surface, (self.x + (self.width - self._text_surface.get_width()) / 2, self.y + 12))
