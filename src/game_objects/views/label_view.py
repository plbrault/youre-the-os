import pygame

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_10

class LabelView(Drawable):
    def __init__(self, label):
        self._label = label
        self._color = Color.WHITE
        self._font = FONT_ARIAL_10
        self._render()

        super().__init__()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        self._font = font
        self._render()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        self._render()

    @property
    def width(self):
        return self.font.size(self._label.text)[0]

    @property
    def height(self):
        return self.font.size(self._label.text)[1]

    def _render(self):
        self._text_surface = self.font.render(self._label.text, False, self._color)

    def draw(self, surface):
        surface.blit(self._text_surface, (self._x, self._y))
