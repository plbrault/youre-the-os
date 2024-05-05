from game_objects.button import Button
from game_objects.views.sort_button_view import SortButtonView

class SortButton(Button):
    def __init__(self, process_manager):
        super().__init__('Sort processes', process_manager.sort_idle_processes, key_bind='s', view_class=SortButtonView)
        self._visible = False
        self.disabled = True

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        self._visible = value

    def update(self, current_time, events):
        if not self.visible:
            events = []
        super().update(current_time, events)
