from collections import deque

import game_monitor
from engine.scene_object import SceneObject
from engine.game_event_type import GameEventType
from engine.random import randint
from scene_objects.views.io_queue_view import IoQueueView

_BLINKING_INTERVAL_MS = 333
_EVENT_PROBABILITY_DENOMINATOR = 3

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

class IoQueue(SceneObject):

    def __init__(self, min_waiting_time_ms, max_waiting_time_ms):
        self._min_waiting_time_ms = min_waiting_time_ms
        self._max_waiting_time_ms = max_waiting_time_ms

        self._subscriber_queue = deque([])
        self._event_count = 0
        self._current_time = 0
        self._last_update_time = 0

        self._display_blink_color = False

        super().__init__(IoQueueView(self))

    def wait_for_event(self, callback):
        self._subscriber_queue.append(
            _IoEventWaiter(self._current_time, callback)
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
        game_monitor.notify_io_event_count(self.event_count)

    def _check_if_clicked_on(self, event):
        if event.type == GameEventType.MOUSE_LEFT_CLICK:
            return self._view.collides(*event.get_property('position'))
        return False

    def _on_click(self):
        self.process_events()

    def update(self, current_time, events):
        self._current_time = current_time

        for event in events:
            if self._check_if_clicked_on(event):
                self._on_click()
            if event.type == GameEventType.KEY_UP:
                if event.get_property('key') == 'space':
                    self.process_events()

        if (
            self._event_count < len(self._subscriber_queue)
            and current_time >=
                self._subscriber_queue[self._event_count].waiting_since + self._max_waiting_time_ms
        ):
            self._last_update_time = current_time
            self._event_count += 1

        elif current_time >= self._last_update_time + self._min_waiting_time_ms:
            self._last_update_time = current_time

            if (
                self._event_count < len(self._subscriber_queue)
                and randint(1, _EVENT_PROBABILITY_DENOMINATOR) == 1
            ):
                self._event_count = randint(
                    self._event_count + 1, len(self._subscriber_queue)
                )
                game_monitor.notify_io_event_count(self._event_count)

        self._display_blink_color = False
        if self._event_count > 0:
            self._display_blink_color = int(current_time / _BLINKING_INTERVAL_MS) % 2 == 1
