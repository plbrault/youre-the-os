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
        color = Color.YELLOW

        if self._process.has_cpu:
            if self._process.current_state_duration < 5:
                if self._process.previous_state_duration < 10:
                    color = Color.YELLOW
                elif self._process.previous_state_duration < 20:
                    color = Color.ORANGE
                elif self._process.previous_state_duration < 30:
                    color = Color.RED
                elif self._process.previous_state_duration < 40:
                    color = Color.DARK_RED
            else:
                color = Color.GREEN
        else:
            if self._process.current_state_duration < 10:
                color = Color.YELLOW
            elif self._process.current_state_duration < 20:
                color = Color.ORANGE
            elif self._process.current_state_duration < 30:
                color = Color.RED
            else:
                color = Color.DARK_RED

        pygame.draw.rect(surface, color, pygame.Rect(self._x, self._y, self.width, self.height))
        pid_text_surface = FONT_ARIAL_10.render('PID ' + str(self._process.pid), False, Color.BLACK)
        surface.blit(pid_text_surface, (self._x + 28, self._y + 5))
