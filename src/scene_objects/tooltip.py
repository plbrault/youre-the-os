from typing import Callable

from engine.drawable import Drawable
from engine.player_input import PlayerInput
from engine.scene_object import SceneObject
from scene_objects.views.tooltip_view import TooltipAlignment, TooltipView

_FADE_IN_DURATION_MS = 250
_FADE_OUT_DURATION_MS = 250


class Tooltip(SceneObject):
    def __init__(self, anchor_view: Drawable, text: str, *,
                 condition: Callable[[], bool],
                 alignment: TooltipAlignment = TooltipAlignment.BELOW):
        super().__init__(TooltipView(self, anchor_view, text, alignment=alignment))
        self._condition = condition
        self._text = text
        self._current_time = 0
        self._fade_direction = None
        self._fade_start_time = 0
        self._fade_start_opacity = 0
        self.visible = False

    @property
    def text(self) -> str:
        return self._text

    @property
    def opacity(self) -> float:
        if self._fade_direction is None:
            return 0
        duration = (
            _FADE_IN_DURATION_MS if self._fade_direction > 0
            else _FADE_OUT_DURATION_MS
        )
        progress = min(
            1,
            (self._current_time - self._fade_start_time) / duration
        )
        if self._fade_direction > 0:
            return (
                self._fade_start_opacity
                + (1 - self._fade_start_opacity) * progress
            )
        return self._fade_start_opacity * (1 - progress)

    def update(self, current_time: int, player_inputs: list[PlayerInput]):
        self._current_time = current_time
        if self._condition():
            if self._fade_direction != 1:
                self._start_fade(1, current_time)
        elif self.opacity > 0:
            if self._fade_direction != -1:
                self._start_fade(-1, current_time)
        else:
            self._fade_direction = None
        self.visible = self._fade_direction == 1 or self.opacity > 0
        super().update(current_time, player_inputs)

    def _start_fade(self, direction, current_time):
        self._fade_start_opacity = self.opacity
        self._fade_direction = direction
        self._fade_start_time = current_time
