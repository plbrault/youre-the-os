from collections import deque
from random import randint

from lib import event_manager
from lib.game_object import GameObject
from lib.game_event_type import GameEventType
from game_objects.views.io_queue_view import IoQueueView

class _IoEventWaiter:
    def __init__(self, current_time, callback):
        self._waiting_since = current_time
        self._callback = callback

    @property
    def waiting_since(self):
        return self._waiting_since

    @property
    def callback(self):
        return self._callback

class IoQueue(GameObject):

    def __init__(self, process_manager):
        self._process_manager = process_manager

        self._subscriber_queue = deque([])
        self._event_count = 0
        self._last_update_time = 0

        self._display_blink_color = False

        super().__init__(IoQueueView(self))

    def wait_for_event(self, callback):
        self._subscriber_queue.append(
            _IoEventWaiter(self._process_manager.game.current_time, callback)
        )

    @property
    def event_count(self):
        return self._event_count

    @property
    def display_blink_color(self):
        return self._display_blink_color

    def process_events(self):
        while self.event_count > 0:
            self._event_count -= 1
            callback = self._subscriber_queue.popleft().callback
            callback()
        event_manager.event_io_queue(self.event_count)

    def _check_if_clicked_on(self, event):
        if event.type == GameEventType.MOUSE_LEFT_CLICK:
            return self._view.collides(*event.get_property('position'))
        return False

    def _on_click(self):
        self.process_events()

    def update(self, current_time, events):
        for event in events:
            if self._check_if_clicked_on(event):
                self._on_click()
            if event.type == GameEventType.KEY_UP:
                if event.get_property('key') == 'space':
                    self.process_events()

        if (
            self._event_count < len(self._subscriber_queue)
            and current_time >= self._subscriber_queue[self._event_count].waiting_since + 5000
        ):
            self._last_update_time = current_time
            self._event_count += 1

        elif current_time >= self._last_update_time + 1000:
            self._last_update_time = current_time

            if self._event_count < len(self._subscriber_queue) and randint(1, 3) == 3:
                self._event_count = randint(
                    self._event_count + 1, len(self._subscriber_queue)
                )
                event_manager.event_io_queue(self._event_count)

        self._display_blink_color = False
        if self._event_count > 0:
            self._display_blink_color = int(current_time / 333) % 2 == 1
