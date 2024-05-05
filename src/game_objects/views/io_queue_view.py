import pygame

from lib.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_SECONDARY_XXSMALL


class IoQueueView(Drawable):
    def __init__(self, io_queue):
        self._io_queue = io_queue
        super().__init__()

    @property
    def width(self):
        return 128

    @property
    def height(self):
        return 32

    def draw(self, surface):
        color = Color.TEAL if self._io_queue.display_blink_color else Color.WHITE
        pygame.draw.rect(surface, color, pygame.Rect(
            self._x, self._y, self.width, self.height))
        text_surface = FONT_SECONDARY_XXSMALL.render(
            'I/O EVENTS (' + str(self._io_queue.event_count) + ')', False, Color.BLACK)
        surface.blit(text_surface, (self._x + 20, self._y + 10))
