from typing import Callable, Type

from engine.drawable import Drawable
from game_objects.button import Button
from game_objects.views.checkbox_view import CheckboxView

class Checkbox(Button):
    def __init__(self,
                 label_text: str = '',
                 *,
                 on_toggle_fn: Callable[[bool], None] = lambda checked: None,
                 key_bind: str = '',
                 view_class: Type[Drawable] = CheckboxView
        ):
        super().__init__(label_text, self._toggle, key_bind=key_bind, view_class=CheckboxView)
        self._checked = False
        self._on_toggle_fn = on_toggle_fn

    def _toggle(self):
        self._checked = not self._checked
        self._on_toggle_fn(self._checked)

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value: bool):
        self._checked = value
