import pygame

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_10

class ProcessView(Drawable):
    def __init__(self, process):
        self._process = process
        super().__init__()

    @property
    def width(self):
        return 64

    @property
    def height(self):
        return 64

    def collides(self, x, y):
        return pygame.Rect(self._x, self._y, self.width, self.height).collidepoint(x, y)

    def draw(self, surface):
        pygame.draw.rect(surface, Color.GREEN, pygame.Rect(self._x, self._y, self.width, self.height))
        status_text_surface = FONT_ARIAL_10.render(self._process.state, False, Color.BLACK)
        cpu_time_text_surface = FONT_ARIAL_10.render('CPU Time: ' + str(self._process.total_cpu_time), False, Color.BLACK)
        idle_time_text_surface = FONT_ARIAL_10.render('Idle Time: ' + str(self._process.total_idle_time), False, Color.BLACK)
        surface.blit(status_text_surface, (self._x + 18, self._y + 5))
        surface.blit(cpu_time_text_surface, (self._x + 2, self._y + 30))
        surface.blit(idle_time_text_surface, (self._x + 2, self._y + 45))
