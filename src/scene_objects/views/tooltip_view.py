from enum import Enum, auto

import pygame

from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_PRIMARY_LARGE
from window_size import WINDOW_WIDTH, WINDOW_HEIGHT

_MARGIN = 3
_PADDING = 10
_MAX_TEXT_WIDTH = 400
_MAX_BACKGROUND_ALPHA = 180
_BORDER_RADIUS = 4
_ARROW_PROTRUSION = 14
_ARROW_HALF_BASE = 9
_ARROW_TOP_OFFSET = 20

_RENDER_SCALE = 4


class TooltipAlignment(Enum):
    BELOW = auto()
    RIGHT = auto()


def _split_long_word(word, font, max_width):
    while font.size(word)[0] > max_width:
        segment = word[:1]
        for char in word[1:]:
            if font.size(segment + char)[0] > max_width:
                break
            segment += char
        yield segment
        word = word[len(segment):]
    yield word


def _wrap_text(text, font, max_width):
    lines = []
    for paragraph in text.split('\n'):
        current_line = ''
        for word in (
            token for word in paragraph.split()
            for token in _split_long_word(word, font, max_width)
        ):
            candidate = word if not current_line else current_line + ' ' + word
            if font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
    return lines


class TooltipView(Drawable):

    def __init__(self, tooltip, anchor_view: Drawable, text: str, *,
                 alignment: TooltipAlignment = TooltipAlignment.BELOW):
        self._tooltip = tooltip
        self._anchor_view = anchor_view
        self._alignment = alignment
        self._line_surfaces = [
            FONT_PRIMARY_LARGE.render(line, False, Color.BLACK)
            for line in _wrap_text(text, FONT_PRIMARY_LARGE, _MAX_TEXT_WIDTH)
        ]
        super().__init__()
        self._bubble_sprite = self._create_bubble_sprite()

    def _create_bubble_sprite(self):
        scale = _RENDER_SCALE
        panel = pygame.Surface(
            (self.width * scale, self.height * scale), pygame.SRCALPHA)
        fill_color = (*Color.CREAM, _MAX_BACKGROUND_ALPHA)
        border_color = (*Color.DARK_YELLOW, _MAX_BACKGROUND_ALPHA)
        if self._alignment == TooltipAlignment.RIGHT:
            body = pygame.Rect(
                _ARROW_PROTRUSION * scale, 0,
                (self.width - _ARROW_PROTRUSION) * scale,
                self.height * scale
            )
        else:
            body = pygame.Rect(
                0, _ARROW_PROTRUSION * scale,
                self.width * scale,
                (self.height - _ARROW_PROTRUSION) * scale
            )
        pygame.draw.rect(
            panel, fill_color, body, 0, border_radius=_BORDER_RADIUS * scale)
        pygame.draw.rect(
            panel, border_color, body, scale,
            border_radius=_BORDER_RADIUS * scale)
        self._draw_arrow(panel, body, fill_color, border_color, scale)
        bubble = pygame.transform.smoothscale(
            panel, (self.width, self.height))
        line_height = FONT_PRIMARY_LARGE.get_linesize()
        for i, line_surface in enumerate(self._line_surfaces):
            bubble.blit(
                line_surface,
                (body.x // scale + _PADDING,
                 body.y // scale + _PADDING + i * line_height)
            )
        return bubble

    @property
    def x(self) -> int:
        if self._alignment == TooltipAlignment.RIGHT:
            x = self._anchor_view.x + self._anchor_view.width + _MARGIN
        else:
            x = self._anchor_view.x + (self._anchor_view.width - self.width) // 2
        return max(_MARGIN, min(x, WINDOW_WIDTH - _MARGIN - self.width))

    @property
    def y(self) -> int:
        if self._alignment == TooltipAlignment.RIGHT:
            y = (
                self._anchor_view.y + self._anchor_view.height // 2
                - _ARROW_TOP_OFFSET
            )
        else:
            y = self._anchor_view.y + self._anchor_view.height + _MARGIN
        return max(_MARGIN, min(y, WINDOW_HEIGHT - _MARGIN - self.height))

    @property
    def width(self) -> int:
        max_line_width = max(
            (surface.get_width() for surface in self._line_surfaces),
            default=0
        )
        arrow_width = (
            _ARROW_PROTRUSION if self._alignment == TooltipAlignment.RIGHT else 0
        )
        return max_line_width + 2 * _PADDING + arrow_width

    @property
    def height(self) -> int:
        arrow_height = 0 if self._alignment == TooltipAlignment.RIGHT else _ARROW_PROTRUSION
        return (
            len(self._line_surfaces) * FONT_PRIMARY_LARGE.get_linesize()
            + 2 * _PADDING + arrow_height
        )

    def draw(self, surface) -> None:
        opacity = self._tooltip.opacity
        if opacity <= 0:
            return
        self._bubble_sprite.set_alpha(round(opacity * 255))
        surface.blit(self._bubble_sprite, (self.x, self.y))

    def _draw_arrow(
            self, panel, body, fill_color, border_color, scale) -> None:
        if self._alignment == TooltipAlignment.RIGHT:
            center = body.y + _ARROW_TOP_OFFSET * scale
            tip = (0, center)
            first_base_corner = (body.x, center - _ARROW_HALF_BASE * scale)
            second_base_corner = (body.x, center + _ARROW_HALF_BASE * scale)
            mouth = pygame.Rect(
                body.x, center - _ARROW_HALF_BASE * scale,
                3 * scale, 2 * _ARROW_HALF_BASE * scale)
        else:
            center = body.centerx
            tip = (center, 0)
            first_base_corner = (
                center - _ARROW_HALF_BASE * scale, body.y)
            second_base_corner = (
                center + _ARROW_HALF_BASE * scale, body.y)
            mouth = pygame.Rect(
                center - _ARROW_HALF_BASE * scale, body.y,
                2 * _ARROW_HALF_BASE * scale, 3 * scale)
        pygame.draw.polygon(panel, fill_color, [
            tip,
            self._into_body(first_base_corner, body, scale),
            self._into_body(second_base_corner, body, scale),
        ])
        pygame.draw.rect(panel, fill_color, mouth)
        pygame.draw.line(panel, border_color, tip, first_base_corner, scale)
        pygame.draw.line(panel, border_color, tip, second_base_corner, scale)

    def _into_body(self, corner, body, scale) -> tuple[int, int]:
        if self._alignment == TooltipAlignment.RIGHT:
            return (body.x + 2 * scale, corner[1])
        return (corner[0], body.y + 2 * scale)
