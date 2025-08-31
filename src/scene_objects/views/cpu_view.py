import pygame

from config.cpu_config import CoreType
from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_SECONDARY_XXSMALL, FONT_SECONDARY_SMALL


class CpuView(Drawable):
    def __init__(self, cpu):
        self._cpu = cpu
        self._id_text_surface = FONT_SECONDARY_XXSMALL.render(
            'CPU ' + str(self._cpu.logical_id), False, Color.WHITE)
        if cpu.core_type != CoreType.STANDARD:
            self._core_type_text_surface = FONT_SECONDARY_SMALL.render(
                'P' if cpu.core_type == CoreType.PERFORMANCE else 'E',
                False, Color.WHITE
            )
        super().__init__()

    @property
    def width(self):
        return 64

    @property
    def height(self):
        return 64

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(
            self._x, self._y, self.width, self.height))
        pygame.draw.rect(surface, Color.BLACK, pygame.Rect(
            self._x + 2, self._y + 2, self.width - 4, self.height - 4))
        if self._cpu.core_type == CoreType.STANDARD:
            surface.blit(
                self._id_text_surface,
                (
                    self._x + self.width / 2 - self._id_text_surface.get_width() / 2,
                    self._y + self.height / 2 - self._id_text_surface.get_height() / 2
                )
            )
        else:
            surface.blit(self._core_type_text_surface,
                (
                    self._x + self.width / 2 - self._core_type_text_surface.get_width() / 2,
                    self._y + 8
                )
            )
            surface.blit(
                self._id_text_surface,
                (
                    self._x + self.width / 2 - self._id_text_surface.get_width() / 2,
                    self._y + self.height - self._id_text_surface.get_height() - 8
                )
            )
