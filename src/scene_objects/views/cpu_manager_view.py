from engine.drawable import Drawable
import pygame
from ui.color import Color


class CpuManagerView(Drawable):
    def __init__(self, cpu_manager):
        self.cpu_manager = cpu_manager
        super().__init__()

    @property
    def width(self):
        return 0

    @property
    def height(self):
        return 0

    def draw(self, surface):
        for rectangle in self.cpu_manager.view_vars['physical_core_rectangles']:
            pygame.draw.rect(
                surface,
                Color.DARK_GREY,
                pygame.Rect(
                    rectangle['x'],
                    rectangle['y'],
                    rectangle['width'],
                    rectangle['height'],
                ),
                2,
            )
