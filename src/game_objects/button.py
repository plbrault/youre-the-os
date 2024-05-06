from typing import Type

from engine.game_event_type import GameEventType
from engine.game_object import GameObject
from engine.drawable import Drawable
from game_objects.views.button_view import ButtonView


class Button(GameObject):

    def __init__(self, text, action_fn,
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

    def _check_if_clicked_on(self, event):
        if event.type == GameEventType.MOUSE_LEFT_CLICK:
            return self._view.collides(*event.get_property('position'))
        if event.type == GameEventType.KEY_UP and event.get_property('key') == self._key_bind:
            return True
        return False

    def _on_click(self):
        self._action_fn()

    def update(self, current_time, events):
        if not self._disabled:
            for event in events:
                if self._check_if_clicked_on(event):
                    self._on_click()
