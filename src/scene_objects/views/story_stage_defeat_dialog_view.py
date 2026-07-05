from os import path

import pygame

from engine.modal_view import ModalView
from ui.color import Color
from ui.fonts import FONT_PRIMARY_LARGE, FONT_PRIMARY_XXLARGE

_image = pygame.image.load(path.join('assets', 'story_stage_defeat.png'))

_IMAGE_SIZE = 400
_PADDING = 30
_TITLE_GAP = 20
_STAGE_GAP = 10
_REASON_GAP = 8
_IMAGE_GAP = 10
_STAT_SPACING = 60
_STATS_TO_BUTTONS_GAP = 20
_BUTTON_BOTTOM_MARGIN = 20


class StoryStageDefeatDialogView(ModalView):
    def __init__(self, dialog):
        self._dialog = dialog
        super().__init__()

        self._image = pygame.transform.scale(_image, (_IMAGE_SIZE, _IMAGE_SIZE))

        title = 'DEFEAT'
        self._title_surface = FONT_PRIMARY_XXLARGE.render(title, False, Color.WHITE)
        self._stage_surface = FONT_PRIMARY_LARGE.render(
            dialog.stage_name.upper(), False, Color.WHITE)
        self._reason_surface = (
            FONT_PRIMARY_LARGE.render(dialog.reason, False, Color.WHITE)
            if dialog.reason is not None else None
        )
        self._uptime_surface = FONT_PRIMARY_LARGE.render(
            'UPTIME: ' + dialog.uptime, False, Color.WHITE)
        self._score_surface = FONT_PRIMARY_LARGE.render(
            'SCORE: ' + str(dialog.score), False, Color.WHITE)

        stats_row_width = (
            self._uptime_surface.get_width()
            + self._score_surface.get_width()
            + _STAT_SPACING
        )
        reason_width = (
            self._reason_surface.get_width() if self._reason_surface is not None else 0
        )
        content_width = max(
            self._image.get_width(),
            self._title_surface.get_width(),
            self._stage_surface.get_width(),
            stats_row_width,
            reason_width,
        )
        self._width = int(content_width + 2 * _PADDING)

    @ModalView.x.setter
    def x(self, value):
        self._x = value
        dialog = self._dialog
        if dialog.standalone:
            dialog.primary_button.view.x = (
                self.x + (self.width / 2) - (dialog.primary_button.view.width / 2))
            return
        dialog.primary_button.view.x = (
            self.x + (self.width / 2) - dialog.primary_button.view.width - 10)
        dialog.main_menu_button.view.x = self.x + (self.width / 2) + 10

    @ModalView.y.setter
    def y(self, value):
        self._y = value
        dialog = self._dialog
        button_y = (
            self.y + self.height
            - dialog.primary_button.view.height - _BUTTON_BOTTOM_MARGIN
        )
        dialog.primary_button.view.y = button_y
        if dialog.standalone:
            return
        dialog.main_menu_button.view.y = button_y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        h = _PADDING
        h += self._title_surface.get_height() + _TITLE_GAP
        h += self._stage_surface.get_height() + _STAGE_GAP
        if self._reason_surface is not None:
            h += self._reason_surface.get_height() + _REASON_GAP
        h += self._image.get_height() + _IMAGE_GAP
        h += self._uptime_surface.get_height()
        h += _STATS_TO_BUTTONS_GAP + self._dialog.primary_button.view.height
        h += _BUTTON_BOTTOM_MARGIN
        return h

    def draw_content(self, surface):
        x = self._x
        y = self._y + _PADDING

        surface.blit(self._title_surface, (
            x + (self.width - self._title_surface.get_width()) / 2, y))
        y += self._title_surface.get_height() + _TITLE_GAP

        surface.blit(self._stage_surface, (
            x + (self.width - self._stage_surface.get_width()) / 2, y))
        y += self._stage_surface.get_height() + _STAGE_GAP

        if self._reason_surface is not None:
            surface.blit(self._reason_surface, (
                x + (self.width - self._reason_surface.get_width()) / 2, y))
            y += self._reason_surface.get_height() + _REASON_GAP

        surface.blit(self._image, (
            x + (self.width - self._image.get_width()) / 2, y))
        y += self._image.get_height() + _IMAGE_GAP

        stats_y = y
        surface.blit(self._uptime_surface, (x + _PADDING, stats_y))
        surface.blit(self._score_surface, (
            x + self.width - _PADDING - self._score_surface.get_width(), stats_y))
