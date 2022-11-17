import pygame

from lib.ui.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_10

class ProcessComponent(Drawable):
    WIDTH = 64
    HEIGHT = 64

    def __init__(self, x, y, process):
        self._x = x
        self._y = y
        self._process = process

    def draw(self, surface):
        pygame.draw.rect(surface, Color.GREEN, pygame.Rect(self._x, self._y, ProcessComponent.WIDTH, ProcessComponent.HEIGHT))

        print("!!!!!!!!!!!!!!!!!!!!!!" + self._process.state)

        text_surface = FONT_ARIAL_10.render(self._process.state, False, Color.BLACK)
        surface.blit(text_surface, (self._x + 18, self._y + 27))
      
