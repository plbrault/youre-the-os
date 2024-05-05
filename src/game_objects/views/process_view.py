from datetime import datetime
from os import path
import pygame

from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_SECONDARY_XXSMALL

_starvation_colors = [
    Color.GREEN,
    Color.YELLOW,
    Color.ORANGE,
    Color.RED,
    Color.DARK_RED,
    Color.DARKER_RED,
    Color.DARK_GREY
]

_starvation_emojis = [
    pygame.image.load(path.join('assets', 'grinning_face_emoji.png')),
    pygame.image.load(path.join('assets', 'slightly_smiling_face_emoji.png')),
    pygame.image.load(path.join('assets', 'neutral_face_emoji.png')),
    pygame.image.load(path.join('assets', 'frowning_face_emoji.png')),
    pygame.image.load(path.join('assets', 'loudly_crying_face_emoji.png')),
    pygame.image.load(path.join('assets', 'cold_face_emoji.png')),
    pygame.image.load(path.join('assets', 'skull_emoji.png')),
]

today = datetime.today().date()
if today.month == 10 and today.day == 31:
    _starvation_emojis[0] = pygame.image.load(
        path.join('assets', 'jack_o_lantern_emoji.png'))

_gracefully_terminated_emoji = pygame.image.load(
    path.join('assets', 'smiling_face_with_halo_emoji.png'))

_waiting_for_io_emoji = pygame.image.load(
    path.join('assets', 'hourglass_not_done_emoji.png'))


class ProcessView(Drawable):
    def __init__(self, process):
        self._process = process
        self._target_x = None
        self._target_y = None
        self._pid_text_surface = FONT_SECONDARY_XXSMALL.render(
            'PID ' + str(self._process.pid), False, Color.BLACK)
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

        if self._process.display_blink_color:
            color = Color.BLUE

        pygame.draw.rect(surface, color, pygame.Rect(
            self._x, self._y, self.width, self.height))
        surface.blit(starvation_emoji_surface, (self._x, self._y + 2))
        surface.blit(self._pid_text_surface, (self._x + 28, self._y + 5))

        if self._process.is_waiting_for_io:
            surface.blit(_waiting_for_io_emoji, (self._x + 27, self._y + 32))

        if self._process.is_progressing_to_happiness:
            pygame.draw.rect(surface, Color.BLUE, pygame.Rect(
                self._x + 2,
                self._y + self.height - 4,
                min(
                    (self.width - 4),
                    (self.width - 4)
                        - (5000 - self._process.current_state_duration)
                        * (self.width - 4) / 5000,
                ),
                2
            ))
