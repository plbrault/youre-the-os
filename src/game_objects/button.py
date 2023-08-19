from lib.game_event_type import GameEventType
from lib.game_object import GameObject
from game_objects.views.button_view import ButtonView


class Button(GameObject):

    def __init__(self, text, action_fn):
        self.text = text
        self._action_fn = action_fn
        super().__init__(ButtonView(self))

    def _check_if_clicked_on(self, event):
        if event.type == GameEventType.MOUSE_LEFT_CLICK:
            return self._view.collides(*event.getProperty('position'))
        return False

    def _on_click(self):
        self._action_fn()

    def update(self, current_time, events):
        for event in events:
            if self._check_if_clicked_on(event):
                self._on_click()
