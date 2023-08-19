import pygame

from lib.drawable import Drawable
from lib.ui.color import Color

class InGameMenuDialogView(Drawable):
    def __init__(self, in_game_menu_dialog):
        self._in_game_menu_dialog = in_game_menu_dialog
        super().__init__()

    @property
    def width(self):
        return self._in_game_menu_dialog.button_width + 8

    @property
    def height(self):
        return 3 * self._in_game_menu_dialog.button_height + 12

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(
            self.x, self.y, self.width, self.height), border_radius=3)
        pygame.draw.rect(
            surface,
            (70,
             70,
             70),
            pygame.Rect(
                self.x + 2,
                self.y + 2,
                self.width - 4,
                self.height - 4),
            border_radius=3)
