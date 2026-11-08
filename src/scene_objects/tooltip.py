from engine.scene_object import SceneObject
from scene_objects.views.tooltip_view import TooltipView

_FADE_IN_DURATION_MS = 250


class Tooltip(SceneObject):

    def __init__(self, anchor_view, text, *, condition, alignment='below'):
        super().__init__(TooltipView(self, anchor_view, text, alignment=alignment))
        self._condition = condition
        self._text = text
        self._current_time = 0
        self._visible_since = None
        self.visible = False

    @property
    def text(self):
        return self._text

    @property
    def opacity(self):
        if self._visible_since is None:
            return 0
        return min(
            1,
            (self._current_time - self._visible_since) / _FADE_IN_DURATION_MS
        )

    def update(self, current_time, player_inputs):
        self._current_time = current_time
        if self._condition():
            if self._visible_since is None:
                self._visible_since = current_time
            self.visible = True
        else:
            self._visible_since = None
            self.visible = False
        super().update(current_time, player_inputs)
