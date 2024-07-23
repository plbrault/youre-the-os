from typing import Optional

from engine.game_event_type import GameEventType
from engine.game_object import GameObject
import game_monitor
from game_objects.page_slot import PageSlot
from game_objects.views.page_view import PageView

_BLINKING_INTERVAL_MS = 200

class Page(GameObject):

    def __init__(self, pid, idx, page_manager):
        self._pid = pid
        self._idx = idx
        self._page_manager = page_manager
        self._stage = page_manager.stage

        self._in_use = False

        self._waiting_to_swap: bool = False
        self._swapping_from: Optional[PageSlot] = None
        self._swapping_to: Optional[PageSlot] = None
        self._started_swap_at: Optional[int] = None
        self._swap_percentage_completed: float = 0
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
    def swap_requested(self) -> bool:
        return self._waiting_to_swap or self.swap_in_progress

    @property
    def swap_percentage_completed(self) -> float:
        return self._swap_percentage_completed

    @property
    def on_disk(self):
        return self._on_disk

    @on_disk.setter
    def on_disk(self, value):
        self._on_disk = value

    @property
    def display_blink_color(self):
        return self._display_blink_color

    def request_swap(self, swap_whole_row : bool = False):
        """The method called when the player clicks on the page."""
        self._page_manager.swap_page(self, swap_whole_row)

    def init_swap(self, swapping_from : PageSlot, swapping_to : PageSlot):
        """The method called by the page manager to set the swap attributes."""
        self._swapping_from = swapping_from
        self._swapping_to = swapping_to
        self._waiting_to_swap = True
        self._swap_percentage_completed = 0

    def start_swap(self, current_time: int):
        """The method called by the page manager to actually start the swap."""
        self._waiting_to_swap = False
        self._started_swap_at = current_time

    def _update_swap(self, current_time):
        """This method is called at each update. If a swap is in progress, it performs
        appropriate checks and operations."""
        if self.swap_in_progress:
            self._swap_percentage_completed = min(1,
                (current_time - self._started_swap_at)
                / self._stage.config.swap_delay_ms
            )
            if self._swap_percentage_completed == 1:
                self.view.set_xy(self._swapping_to.view.x, self._swapping_to.view.y)
                self._swapping_from.page = None
                self._swapping_to.page = self
                self._swapping_to.incoming_page = None
                self._swapping_from = None
                self._swapping_to = None
                self._started_swap_at = None
                self._on_disk = not self._on_disk
                self._swap_percentage_completed = 0
                game_monitor.notify_page_swap(self.pid, self.idx, self.on_disk)

    def _check_if_clicked_on(self, event):
        if event.type in [GameEventType.MOUSE_LEFT_CLICK, GameEventType.MOUSE_LEFT_DRAG]:
            return self._view.collides(*event.get_property('position'))
        return False

    def _on_click(self, shift_down : bool):
        self.request_swap(shift_down)

    def update(self, current_time, events):
        for event in events:
            if self._check_if_clicked_on(event):
                self._on_click(event.get_property('shift'))

        self._update_swap(current_time)
        if self.in_use and self.on_disk:
            self._display_blink_color = int(current_time / _BLINKING_INTERVAL_MS) % 2 == 1
        else:
            self._display_blink_color = False
