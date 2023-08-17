from lib.game_event_type import GameEventType
from lib.game_object import GameObject
from game_objects.views.page_view import PageView
from lib import event_manager

class Page(GameObject):

    Pages = {}

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

    @property
    def in_swap(self):
        return self._in_swap

    @property
    def display_blink_color(self):
        return self._display_blink_color

    @in_use.setter
    def in_use(self, value):
        if self._in_use != value:
            event_manager.event_page_use(self._pid, self._idx, value)
        self._in_use = value

    def _check_if_clicked_on(self, event):
        if event.type == GameEventType.MOUSE_LEFT_CLICK or event.type == GameEventType.MOUSE_LEFT_DRAG:
            return self._view.collides(*event.getProperty('position'))
        return False

    def onClick(self):
        self._page_manager.swap_page(self)

    def update(self, current_time, events):
        for event in events:
            if self._check_if_clicked_on(event):
                self.onClick()

        if self.in_use and self.in_swap:
            self._display_blink_color = (int(current_time / 200) % 2 == 1)
        else:
            self._display_blink_color = False
