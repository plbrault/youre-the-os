import pygame

from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_SECONDARY_SMALL

_checkbox_image = pygame.image.load('assets/checkbox.png')
_label_font = FONT_SECONDARY_SMALL

_CHECKBOX_WIDTH = 16
_CHECKBOX_RIGHT_MARGIN = 4


class CheckboxView(Drawable):
    def __init__(self, checkbox):
        self._checkbox = checkbox
        self._text_surface = _label_font.render(
            self._checkbox.text.upper(), True, Color.LIME_GREEN)
        super().__init__()

    @property
    def width(self):
        return _CHECKBOX_WIDTH + _CHECKBOX_RIGHT_MARGIN + self._text_surface.get_width()

    @property
    def height(self):
        return 16

    def draw(self, surface):
        pygame.draw.rect(surface, Color.LIME_GREEN, pygame.Rect(
            self._x, self._y, _CHECKBOX_WIDTH, self.height), 2)
        if self._checkbox.checked:
            surface.blit(_checkbox_image, (
                self._x + 2, self._y + 2))
        surface.blit(self._text_surface, (
            self._x + _CHECKBOX_WIDTH + _CHECKBOX_RIGHT_MARGIN, self._y - 2))
