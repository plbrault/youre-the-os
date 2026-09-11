import pygame

from engine.drawable import Drawable
from scene_objects.views.view_utils import ViewUtils
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
        view_utils = ViewUtils()
        color = Color.TEAL if self._io_queue.display_blink_color else Color.WHITE
        pygame.draw.rect(surface, color, pygame.Rect(
            self._x, self._y, self.width, self.height))
        text_surface = FONT_SECONDARY_XXSMALL.render(
            'I/O EVENTS (' + str(self._io_queue.event_count) + ')', False, view_utils.contrasted_color(color))
        surface.blit(text_surface, (self._x + 20, self._y + 10))
