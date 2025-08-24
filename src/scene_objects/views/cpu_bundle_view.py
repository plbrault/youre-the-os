import pygame

from engine.drawable import Drawable
from ui.color import Color


class CpuBundleView(Drawable):
    def __init__(self, cpu_bundle):
        self._cpu_bundle = cpu
        super().__init__()

    @property
    def width(self):
        return 136

    @property
    def height(self):
        return 72

    def draw(self, surface):
        pygame.draw.rect(surface, Color.LIGHT_GREY, pygame.Rect(
            self._x, self._y, self.width, self.height))
        pygame.draw.rect(surface, Color.BLACK, pygame.Rect(
            self._x + 2, self._y + 2, self.width - 4, self.height - 4))
        surface.blit(self._text_surface, (self._x + 18, self._y + 27))
