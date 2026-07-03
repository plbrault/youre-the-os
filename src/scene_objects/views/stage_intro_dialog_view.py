from os import path

import pygame

from engine.modal_view import ModalView
from ui.color import Color
from ui.fonts import (
    FONT_PRIMARY_XLARGE, FONT_PRIMARY_LARGE, FONT_PRIMARY_MEDIUM,
)

_BADGE_SIZE = 64
_BADGE_SPACING = 16
_TIMER_ICON_SIZE = 40
_TIMER_LABEL_SPACING = 4

_skull = pygame.image.load(path.join('assets', 'skull_emoji.png'))
_crown = pygame.image.load(path.join('assets', 'crown_emoji.png'))
_timer = pygame.image.load(path.join('assets', 'timer.png'))


class StageIntroDialogView(ModalView):
    WIDTH = 480
    PADDING = 30
    HEADING_SPACING = 24
    ITEM_SPACING = 4
    SECTION_SPACING = 16
    BUTTON_BOTTOM_MARGIN = 40

    def __init__(self, dialog):
        self._dialog = dialog
        super().__init__()
        self._title_surface = FONT_PRIMARY_XLARGE.render(
            self._dialog.title, True, Color.WHITE)
        self._section_headings = []
        self._section_items = []
        for section in self._dialog.sections:
            heading_surface = FONT_PRIMARY_LARGE.render(
                section.heading, True, Color.WHITE)
            self._section_headings.append(heading_surface)
            items = []
            for item in section.items:
                item_surface = FONT_PRIMARY_MEDIUM.render(
                    '\u2022 ' + item, True, Color.WHITE)
                items.append(item_surface)
            self._section_items.append(items)
        self._badge_surfaces = []
        for badge in self._dialog.badges:
            if hasattr(badge, 'minutes'):
                self._badge_surfaces.append(self._render_timer_badge(badge))
            else:
                self._badge_surfaces.append(self._render_badge(badge))

    def _render_badge(self, badge):
        surface = pygame.Surface((_BADGE_SIZE, _BADGE_SIZE))
        surface.fill(Color.DARK_GREY)
        surface.blit(_skull, (0, 2))
        if badge.is_priority:
            surface.blit(_crown, (2, 34))
        number_surface = FONT_PRIMARY_XLARGE.render(str(badge.number), True, Color.LIME_GREEN)
        surface.blit(number_surface, (
            _BADGE_SIZE - number_surface.get_width() - 4,
            (_BADGE_SIZE - number_surface.get_height()) // 2,
        ))
        return surface

    def _render_timer_badge(self, badge):
        icon = pygame.transform.scale(_timer, (_TIMER_ICON_SIZE, _TIMER_ICON_SIZE))
        label_surface = FONT_PRIMARY_MEDIUM.render(
            f'{badge.minutes} min.', True, Color.WHITE)
        width = max(icon.get_width(), label_surface.get_width())
        height = icon.get_height() + _TIMER_LABEL_SPACING + label_surface.get_height()
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.blit(icon, ((width - icon.get_width()) // 2, 0))
        surface.blit(label_surface, (
            (width - label_surface.get_width()) // 2,
            icon.get_height() + _TIMER_LABEL_SPACING,
        ))
        return surface

    @ModalView.x.setter
    def x(self, value):
        self._x = value
        self._dialog.start_button.view.x = (
            self.x + (self.width - self._dialog.start_button.view.width) / 2)

    @ModalView.y.setter
    def y(self, value):
        self._y = value
        self._dialog.start_button.view.y = (
            self.y + self.height - self._dialog.start_button.view.height
            - self.BUTTON_BOTTOM_MARGIN)

    @property
    def width(self):
        return self.WIDTH

    @property
    def height(self):
        y = self.PADDING
        y += self._title_surface.get_height() + self.HEADING_SPACING
        for i, heading_surface in enumerate(self._section_headings):
            y += heading_surface.get_height() + self.ITEM_SPACING
            for item_surface in self._section_items[i]:
                y += item_surface.get_height() + self.ITEM_SPACING
            y += self.SECTION_SPACING
        if self._badge_surfaces:
            y += max(s.get_height() for s in self._badge_surfaces) + 40
        y += self.BUTTON_BOTTOM_MARGIN
        y += self._dialog.start_button.view.height
        y += self.BUTTON_BOTTOM_MARGIN
        return y

    def draw_content(self, surface):
        x = self.x + self.PADDING
        y = self.y + self.PADDING

        surface.blit(self._title_surface, (
            self.x + (self.width - self._title_surface.get_width()) / 2, y))
        y += self._title_surface.get_height() + self.HEADING_SPACING

        for i, heading_surface in enumerate(self._section_headings):
            surface.blit(heading_surface, (x, y))
            y += heading_surface.get_height() + self.ITEM_SPACING
            for item_surface in self._section_items[i]:
                surface.blit(item_surface, (x + self.ITEM_SPACING * 4, y))
                y += item_surface.get_height() + self.ITEM_SPACING
            y += self.SECTION_SPACING

        if self._badge_surfaces:
            button_top = (
                self.y + self.height
                - self.BUTTON_BOTTOM_MARGIN
                - self._dialog.start_button.view.height
            )
            badge_band_top = y
            total_badge_width = (
                sum(s.get_width() for s in self._badge_surfaces)
                + (len(self._badge_surfaces) - 1) * _BADGE_SPACING
            )
            badge_x = self.x + (self.width - total_badge_width) // 2
            for badge_surface in self._badge_surfaces:
                badge_y = badge_band_top + (
                    button_top - badge_band_top - badge_surface.get_height()) // 2
                surface.blit(badge_surface, (badge_x, badge_y))
                badge_x += badge_surface.get_width() + _BADGE_SPACING
