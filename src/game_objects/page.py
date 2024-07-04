from typing import Optional

from engine.game_event_type import GameEventType
from engine.game_object import GameObject
from game_objects.page_slot import PageSlot
from game_objects.views.page_view import PageView

_BLINKING_INTERVAL_MS = 200

class Page(GameObject):

    def __init__(self, pid, idx, page_manager):
        self._pid = pid
        self._idx = idx
        self._page_manager = page_manager

        self._in_use = False

        self._swap_queued: bool = False
        self._swapping_from: Optional[PageSlot] = None
        self._swapping_to: Optional[PageSlot] = None
        self._started_swap_at: Optional[int] = None
        self._on_disk = False

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
    def swap_in_progress(self) -> bool:
        return self._started_swap_at is not None

    @property
    def swapping_from(self) -> Optional[PageSlot]:
        return self._swapping_from

    @swapping_from.setter
    def swapping_from(self, value: Optional[PageSlot]):
        self._swapping_from = value

    @property
    def swapping_to(self) -> Optional[PageSlot]:
        return self._swapping_to

    @swapping_to.setter
    def swapping_to(self, value: Optional[PageSlot]):
        self._swapping_to = value

    @property
    def started_swap_at(self) -> Optional[int]:
        return self._started_swap_at

    @started_swap_at.setter
    def started_swap_at(self, value: Optional[int]):
        self._started_swap_at = value

    @property
    def swap_percentage_completed(self) -> float:
        if not self.swap_in_progress:
            return 0
        return (self._page_manager.stage.current_time - self._started_swap_at) / self._page_manager.stage.config.swap_delay_ms

    @property
    def on_disk(self):
        return self._on_disk

    @on_disk.setter
    def on_disk(self, value):
        self._on_disk = value

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

        if self.in_use and self.on_disk:
            self._display_blink_color = int(current_time / _BLINKING_INTERVAL_MS) % 2 == 1
        else:
            self._display_blink_color = False
