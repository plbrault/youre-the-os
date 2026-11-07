from typing import Callable, Type

from engine.player_input_type import PlayerInputType
from engine.scene_object import SceneObject
from engine.drawable import Drawable
from scene_objects.views.button_view import ButtonView


class Button(SceneObject):

    def __init__(self, text, action_fn: Callable,
                 *, key_bind: str = '', view_class: Type[Drawable] = ButtonView
        ):
        self.text = text
        self._action_fn = action_fn
        self._key_bind = key_bind
        super().__init__(view_class(self))

        self._disabled = False

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool):
        self._disabled = value

    def _check_if_clicked_on(self, player_input):
        if player_input.type == PlayerInputType.MOUSE_LEFT_CLICK:
            return self._view.collides(*player_input.get_property('position'))
        if (
            player_input.type == PlayerInputType.KEY_UP
            and player_input.get_property('key') == self._key_bind
        ):
            return True
        return False

    def _on_click(self):
        self._action_fn()

    def update(self, current_time, player_inputs):
        if not self._disabled:
            for player_input in player_inputs:
                if self._check_if_clicked_on(player_input):
                    self._on_click()
