import pygame

from lib.drawable import Drawable

class ProcessSlotView(Drawable):
    def __init__(self):
        super().__init__()

    @property
    def width(self):
        return 64

    @property
    def height(self):
        return 64

    def draw(self, surface):
        pass
