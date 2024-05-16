import pygame

from engine.drawable import Drawable
from ui.color import Color


class CheckboxView(Drawable):
    def __init__(self, checkbox):
        self._checkbox = checkbox
        super().__init__()

    @property
    def width(self):
        return 32

    @property
    def height(self):
        return 32

    def draw(self, surface):
        pygame.draw.rect(surface, Color.GREEN, pygame.Rect(
            self._x, self._y, self.width, self.height))
