import pygame

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_MEDIUM

class ButtonView(Drawable):
    def __init__(self, button):
        self._button = button
        super().__init__()

    @property
    def width(self):
        return 0

    @property
    def height(self):
        return 0

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self.x, self.y, 200, 50), border_radius=3)
