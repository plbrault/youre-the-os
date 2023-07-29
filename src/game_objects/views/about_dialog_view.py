from os import path
import pygame

from lib.drawable import Drawable
from lib.ui.fonts import FONT_PRIMARY_LARGE, FONT_SECONDARY_MEDIUM
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_XXLARGE, FONT_SECONDARY_MEDIUM

class AboutDialogView(Drawable):
    def __init__(self, about_dialog):
        self.about_dialog = about_dialog
        super().__init__()
        
    @property
    def width(self):
        return 520

    @property
    def height(self):
        return 460

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self.x, self.y, self.width, self.height), border_radius=3)
        pygame.draw.rect(surface, (70, 70, 70), pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4), border_radius=3)
