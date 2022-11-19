import pygame
from pygame_emojis import load_emoji

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_10

_starvation_colors = [
    Color.GREEN,
    Color.YELLOW,
    Color.ORANGE,
    Color.RED,
    Color.DARK_RED,
    Color.DARKER_RED,
    Color.DARK_GREY
]

_starvation_emoji_size = (32, 32)
_starvation_emojis = [
    load_emoji('😀', _starvation_emoji_size),
    load_emoji('🙂', _starvation_emoji_size),
    load_emoji('😐', _starvation_emoji_size),
    load_emoji('☹️', _starvation_emoji_size),
    load_emoji('😭', _starvation_emoji_size),
    load_emoji('🥶', _starvation_emoji_size),
    load_emoji('💀', _starvation_emoji_size),
]

_blocked_emoji = load_emoji('⏳', (32, 32))

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
        color = _starvation_colors[self._process.starvation_level]
        pygame.draw.rect(surface, color, pygame.Rect(self._x, self._y, self.width, self.height))

        starvation_emoji_surface = _starvation_emojis[self._process.starvation_level]
        surface.blit(starvation_emoji_surface, (self._x + 2, self._y + 2))

        pid_text_surface = FONT_ARIAL_10.render('PID ' + str(self._process.pid), False, Color.BLACK)
        surface.blit(pid_text_surface, (self._x + 32, self._y + 5))

        if self._process.is_blocked:
            surface.blit(_blocked_emoji, (self._x + 28, self._y + 32))
