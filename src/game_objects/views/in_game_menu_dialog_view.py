import pygame

from engine.drawable import Drawable
from ui.color import Color

class InGameMenuDialogView(Drawable):
    def __init__(self, in_game_menu_dialog):
        self._in_game_menu_dialog = in_game_menu_dialog
        super().__init__()

    @Drawable.x.setter
    def x(self, value):
        self._x = value
        self._in_game_menu_dialog.restart_button.view.x = self.x + (
            self.width - self._in_game_menu_dialog.restart_button.view.width
        ) / 2
        self._in_game_menu_dialog.main_menu_button.view.x = self.x + (
            self.width - self._in_game_menu_dialog.main_menu_button.view.width
        ) / 2
        self._in_game_menu_dialog.close_menu_button.view.x = self.x + (
            self.width - self._in_game_menu_dialog.close_menu_button.view.width
        ) / 2

    @Drawable.y.setter
    def y(self, value):
        self._y = value
        y = self.y + 4
        self._in_game_menu_dialog.restart_button.view.y = y
        y += self._in_game_menu_dialog.restart_button.view.height + 2
        self._in_game_menu_dialog.main_menu_button.view.y = y
        y += self._in_game_menu_dialog.main_menu_button.view.height + 2
        self._in_game_menu_dialog.close_menu_button.view.y = y

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
