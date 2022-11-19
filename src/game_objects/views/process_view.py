import pygame
from pygame_emojis import load_emoji

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

    def draw(self, surface):
        color = Color.YELLOW

        if self._process.starvation_level == 0:
            color = Color.GREEN
        elif self._process.starvation_level == 1:
            color = Color.YELLOW
        elif self._process.starvation_level == 2:
            color = Color.ORANGE
        elif self._process.starvation_level == 3:
            color = Color.RED
        elif self._process.starvation_level == 4:
            color = Color.DARK_RED
        elif self._process.starvation_level == 5:
            color = Color.DARKER_RED

        pygame.draw.rect(surface, color, pygame.Rect(self._x, self._y, self.width, self.height))
        pid_text_surface = FONT_ARIAL_10.render('PID ' + str(self._process.pid), False, Color.BLACK)
        surface.blit(pid_text_surface, (self._x + 28, self._y + 5))

        if self._process.is_blocked:
            emoji_surface = load_emoji('⏳', (32, 32))
            surface.blit(emoji_surface, (self._x + 16, self._y + 20))
