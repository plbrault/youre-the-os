import pygame

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_10

class CpuView(Drawable):
    def __init__(self, cpu):
        super().__init__()

        self._cpu = cpu
        self._text_surface = FONT_ARIAL_10.render('CPU ' + str(self._cpu.cpu_id), False, Color.WHITE)

    def width(self):
        return 64

    def height(self):
        return 64

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self._x, self._y, self.width, self.height))
        pygame.draw.rect(surface, Color.BLACK, pygame.Rect(self._x + 2, self._y + 2, self.width - 4, self.height - 4))
        surface.blit(self._text_surface, (self._x + 18, self._y + 27))
