from game_objects.button import Button
from game_objects.views.sort_button_view import SortButtonView

_BLINKING_INTERVAL_MS = 500

class SortButton(Button):
    def __init__(self, process_manager):
        super().__init__('Sort', self._action, key_bind='s', view_class=SortButtonView)
        self._process_manager = process_manager
        self._visible = False
        self._became_visible_at = 0
        self._blinking = False
        self._blinking_hidden = False

    def _action(self):
        self._blinking = self._blinking_hidden = False
        self._process_manager.sort_idle_processes()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        self._visible = value
        self._blinking_hidden = False
        if self._visible:
            self._blinking = True
            self._became_visible_at = self._process_manager.game.current_time
        else:
            self._blinking = False
            self._became_visible_at = 0

    @property
    def blinking_hidden(self):
        return self._blinking_hidden

    def update(self, current_time, events):
        if not self.visible:
            events = []
        elif self._blinking:
            visible_duration = current_time - self._became_visible_at
            new_blinking_hidden = bool(int(visible_duration / _BLINKING_INTERVAL_MS) % 2 == 1)
            if new_blinking_hidden != self._blinking_hidden:
                self._blinking_hidden = new_blinking_hidden
        super().update(current_time, events)
