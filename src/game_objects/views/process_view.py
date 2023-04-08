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

_gracefully_terminated_emoji = load_emoji('😇', _starvation_emoji_size)

_blocked_emoji = load_emoji('⏳', (32, 32))

class ProcessView(Drawable):
    def __init__(self, process):
        self._process = process
        self._target_x = None
        self._target_y = None
        super().__init__()

    @property
    def width(self):
        return 64

    @property
    def height(self):
        return 64

    @property
    def target_x(self):
        return self._target_x

    @target_x.setter
    def target_x(self, target_x):
        self._target_x = target_x

    @property
    def target_y(self):
        return self._target_y

    @target_y.setter
    def target_y(self, target_y):
        self._target_y = target_y

    def set_target_xy(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y

    def draw(self, surface):
        if self._process.has_ended and self._process.starvation_level == 0:
            color = Color.LIGHT_BLUE
            starvation_emoji_surface = _gracefully_terminated_emoji
        else:
            color = _starvation_colors[self._process.starvation_level]
            starvation_emoji_surface = _starvation_emojis[self._process.starvation_level]
        
        pid_text_surface = FONT_ARIAL_10.render('PID ' + str(self._process.pid), False, Color.BLACK)  

        pygame.draw.rect(surface, color, pygame.Rect(self._x, self._y, self.width, self.height))
        surface.blit(starvation_emoji_surface, (self._x + 2, self._y + 2))
        surface.blit(pid_text_surface, (self._x + 32, self._y + 5))

        if self._process.is_blocked:
            surface.blit(_blocked_emoji, (self._x + 28, self._y + 32))
