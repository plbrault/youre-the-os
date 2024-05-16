import pygame

from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_SECONDARY_MEDIUM

_checkbox_image = pygame.image.load('assets/checkbox.png')


class CheckboxView(Drawable):
    def __init__(self, checkbox):
        self._checkbox = checkbox
        super().__init__()

    @property
    def width(self):
        return 16

    @property
    def height(self):
        return 16

    def draw(self, surface):
        pygame.draw.rect(surface, Color.LIME_GREEN, pygame.Rect(
            self._x, self._y, self.width, self.height), 2)
        if self._checkbox.checked:
            surface.blit(_checkbox_image, (self._x + 2, self._y + 2))
