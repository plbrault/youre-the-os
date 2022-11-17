import pygame

from lib.ui.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_10

class CpuComponent(Drawable):
    WIDTH = 64
    HEIGHT = 64

    def __init__(self, x, y, cpu_id):
        self._x = x
        self._y = y
        self._cpu_id = cpu_id
        self._text_surface = FONT_ARIAL_10.render('CPU ' + str(cpu_id), False, Color.WHITE)

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self._x, self._y, CpuComponent.WIDTH, CpuComponent.HEIGHT))
        pygame.draw.rect(surface, Color.BLACK, pygame.Rect(self._x + 2, self._y + 2, CpuComponent.WIDTH - 4, CpuComponent.HEIGHT - 4))
        surface.blit(self._text_surface, (self._x + 18, self._y + 27))
      
