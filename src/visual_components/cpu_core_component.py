import pygame

from lib.ui.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_10

class CpuCoreComponent(Drawable):
    _x = 0
    _y = 0
    _cpu_id = 1
    _text_surface = None

    def __init__(self, x, y, cpu_id):
        self._x = x
        self._y = y
        self._cpu_id = cpu_id
        self._text_surface = FONT_ARIAL_10.render('CPU ' + str(cpu_id), False, Color.GREEN)

    def draw(self, surface):
        pygame.draw.rect(surface, Color.GREEN, pygame.Rect(self._x, self._y, 64, 64))
        pygame.draw.rect(surface, Color.BLACK, pygame.Rect(self._x + 2, self._y + 2, 60, 60))
        surface.blit(self._text_surface, (100, 100))
      
