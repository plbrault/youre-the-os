from os import path
import pygame

from engine.modal_view import ModalView
from ui.color import Color
from ui.fonts import FONT_PRIMARY_LARGE, FONT_PRIMARY_XXLARGE

_shutdown_image = pygame.image.load(path.join('assets', 'shutdown.jpg'))


class GameOverDialogView(ModalView):
    def __init__(self, game_over_dialog):
        self._game_over_dialog = game_over_dialog
        super().__init__()

        self._image = _shutdown_image

        self._main_text_surface = FONT_PRIMARY_XXLARGE.render(
            'YOU GOT REBOOTED!', False, Color.WHITE)
        self._uptime_text_surface = FONT_PRIMARY_LARGE.render(
            'UPTIME: ' + game_over_dialog.uptime, False, Color.WHITE)
        self._stage_name_text_surface = FONT_PRIMARY_LARGE.render(
            game_over_dialog.stage_name.upper(), False, Color.WHITE)
        self._score_text_surface = FONT_PRIMARY_LARGE.render(
            'SCORE: ' + str(game_over_dialog.score), False, Color.WHITE)

    @ModalView.x.setter
    def x(self, value):
        self._x = value
        dialog = self._game_over_dialog
        if dialog.standalone:
            dialog._play_again_button.view.x = (
                self.x + (self.width / 2) - (dialog._play_again_button.view.width / 2))
        else:
            dialog._play_again_button.view.x = (
                self.x + (self.width / 2) - dialog._play_again_button.view.width - 10)
            dialog._main_menu_button.view.x = self.x + (self.width / 2) + 10

    @ModalView.y.setter
    def y(self, value):
        self._y = value
        dialog = self._game_over_dialog
        if dialog.standalone:
            dialog._play_again_button.view.y = (
                self.y + self.height - dialog._play_again_button.view.height - 20)
        else:
            dialog._play_again_button.view.y = (
                self.y + self.height - dialog._play_again_button.view.height - 20)
            dialog._main_menu_button.view.y = (
                self.y + self.height - dialog._play_again_button.view.height - 20)

    @property
    def width(self):
        return self._image.get_width() + 4

    @property
    def height(self):
        return 680

    def draw_content(self, surface):
        surface.blit(self._main_text_surface, (self.x + (self.width -
                     self._main_text_surface.get_width()) / 2, self.y + 20))

        surface.blit(self._image, (self._x + 2, self._y +
                     self._main_text_surface.get_height() + 40))

        surface.blit(
            self._uptime_text_surface,
            (self.x +
             20,
             self.y +
             self._main_text_surface.get_height() +
             self._image.get_height() +
             80))
        surface.blit(
            self._stage_name_text_surface,
            (self.x +
            (self.width - self._stage_name_text_surface.get_width()) /
             2,
             self.y +
             self._main_text_surface.get_height() +
             self._image.get_height() +
             80))
        surface.blit(
            self._score_text_surface,
            (self.x +
             self.width -
             self._score_text_surface.get_width() -
             20,
             self.y +
             self._main_text_surface.get_height() +
             self._image.get_height() +
             80))
