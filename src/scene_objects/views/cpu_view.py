import pygame

from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_SECONDARY_XXSMALL


class CpuView(Drawable):
    def __init__(self, cpu):
        self._cpu = cpu
        self._text_surface = FONT_SECONDARY_XXSMALL.render(
            'CPU ' + str(self._cpu.id), False, Color.WHITE)
        super().__init__()

    @property
    def width(self):
        return 64

    @property
    def height(self):
        return 64

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(
            self._x, self._y, self.width, self.height))
        pygame.draw.rect(surface, Color.BLACK, pygame.Rect(
            self._x + 2, self._y + 2, self.width - 4, self.height - 4))
        surface.blit(self._text_surface, (self._x + 18, self._y + 27))
