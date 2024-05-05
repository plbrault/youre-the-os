import pygame

from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_PRIMARY_LARGE


class SortButtonView(Drawable):
    def __init__(self, button):
        self._button = button
        super().__init__()

        self._min_width = 0
        self._text_surface = FONT_PRIMARY_LARGE.render(
            self._button.text.upper(), False, Color.BLACK)
        self._text_surface_disabled = FONT_PRIMARY_LARGE.render(
            self._button.text.upper(), False, Color.GREY)

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
        return self._text_surface.get_height()

    def draw(self, surface):
        if self._button.visible and not self._button.blinking_hidden:
            background_color = Color.LIGHT_BLUE
            text_surface = self._text_surface

            if self._button.disabled:
                background_color = Color.DARK_GREY
                text_surface = self._text_surface_disabled

            pygame.draw.rect(
                surface,
                background_color,
                pygame.Rect(
                    self.x,
                    self.y,
                    self.width,
                    self.height),
                border_radius=3)
            surface.blit(text_surface, (self.x + (self.width -
                        text_surface.get_width()) / 2, self.y))
