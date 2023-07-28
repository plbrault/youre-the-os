from os import path
import pygame

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_LARGE, FONT_PRIMARY_XLARGE, FONT_PRIMARY_XXLARGE

class InGameMenuDialogView(Drawable):
    def __init__(self, game_over_dialog):
        self._game_over_dialog = game_over_dialog
        super().__init__()

    @property
    def width(self):
        return self._game_over_dialog.button_width + 8

    @property
    def height(self):
        return 3 * self._game_over_dialog.button_height + 12

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self.x, self.y, self.width, self.height), border_radius=3)
        pygame.draw.rect(surface, (70, 70, 70), pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4), border_radius=3)
