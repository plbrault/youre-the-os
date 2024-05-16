from engine.game_event_type import GameEventType
from engine.game_object import GameObject
from game_objects.views.page_view import PageView

_BLINKING_INTERVAL_MS = 200

class Page(GameObject):

    def __init__(self, pid, idx, page_manager):
        self._pid = pid
        self._idx = idx
        self._page_manager = page_manager

        self._in_use = False
        self._in_swap = False
        self._display_blink_color = False

        super().__init__(PageView(self))

    @property
    def pid(self):
        return self._pid

    @property
    def idx(self):
        return self._idx

    @property
    def in_use(self):
        return self._in_use

    @in_use.setter
    def in_use(self, value):
        self._in_use = value

    @property
    def in_swap(self):
        return self._in_swap

    @in_swap.setter
    def in_swap(self, value):
        self._in_swap = value

    @property
    def display_blink_color(self):
        return self._display_blink_color

    def swap(self, swap_whole_row : bool = False):
        self._page_manager.swap_page(self, swap_whole_row)

    def _check_if_clicked_on(self, event):
        if event.type in [GameEventType.MOUSE_LEFT_CLICK, GameEventType.MOUSE_LEFT_DRAG]:
            return self._view.collides(*event.get_property('position'))
        return False

    def _on_click(self, shift_down : bool):
        self.swap(shift_down)

    def update(self, current_time, events):
        for event in events:
            if self._check_if_clicked_on(event):
                self._on_click(event.get_property('shift'))

        if self.in_use and self.in_swap:
            self._display_blink_color = int(current_time / _BLINKING_INTERVAL_MS) % 2 == 1
        else:
            self._display_blink_color = False
