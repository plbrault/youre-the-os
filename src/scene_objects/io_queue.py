from collections import deque

import game_monitor
from constants import ONE_SECOND
from engine.scene_object import SceneObject
from engine.player_input_type import PlayerInputType
from engine.random import randint
from scene_objects.views.io_queue_view import IoQueueView

_BLINKING_INTERVAL_MS = 333
_IO_EVENT_PROBABILITY_DENOMINATOR = 3
_IO_EVENTS_TOOLTIP_DELAY_MS = 30 * ONE_SECOND

class _IoEventWaiter:
    def __init__(self, current_time, on_arrival_callback, on_delivery_callback):
        self._waiting_since = current_time
        self._on_arrival_callback = on_arrival_callback
        self._on_delivery_callback = on_delivery_callback

    @property
    def waiting_since(self):
        return self._waiting_since

    @property
    def on_arrival_callback(self):
        return self._on_arrival_callback

    @property
    def on_delivery_callback(self):
        return self._on_delivery_callback

class IoQueue(SceneObject):

    def __init__(self, min_waiting_time_ms, max_waiting_time_ms):
        self._min_waiting_time_ms = min_waiting_time_ms
        self._max_waiting_time_ms = max_waiting_time_ms

        self._subscriber_queue = deque([])
        self._io_event_count = 0
        self._wasted_action_count = 0
        self._current_time = 0
        self._last_io_event_check_time = 0

        self._display_blink_color = False

        self._io_events_available_since = None
        self._tooltip_was_acknowledged = False

        super().__init__(IoQueueView(self))

    def wait_for_io_event(self, current_time, on_arrival_callback, on_delivery_callback):
        waiter = _IoEventWaiter(current_time, on_arrival_callback, on_delivery_callback)
        self._subscriber_queue.append(waiter)
        return waiter

    def cancel_waiter(self, waiter):
        try:
            waiter_index = self._subscriber_queue.index(waiter)
        except ValueError:
            return
        self._subscriber_queue.remove(waiter)
        if waiter_index < self._io_event_count:
            self._io_event_count -= 1
            game_monitor.notify_io_event_count(self.io_event_count)
        if self.io_event_count == 0:
            self._io_events_available_since = None

    @property
    def io_event_count(self):
        return self._io_event_count

    @property
    def wasted_action_count(self):
        return self._wasted_action_count

    @property
    def display_blink_color(self):
        return self._display_blink_color

    @property
    def should_display_tooltip(self):
        return (
            self._io_events_available_since is not None
            and not self._tooltip_was_acknowledged
            and self._current_time
                >= self._io_events_available_since + _IO_EVENTS_TOOLTIP_DELAY_MS
        )

    def handle_player_action(self):
        if self.io_event_count == 0:
            self._wasted_action_count += 1
            return
        while self.io_event_count > 0:
            self._io_event_count -= 1
            waiter = self._subscriber_queue.popleft()
            waiter.on_delivery_callback()
        if (
            self._io_events_available_since is not None
            and self._current_time
                >= self._io_events_available_since + _IO_EVENTS_TOOLTIP_DELAY_MS
        ):
            self._tooltip_was_acknowledged = True
        self._io_events_available_since = None
        game_monitor.notify_io_event_count(self.io_event_count)

    def _check_if_clicked_on(self, player_input):
        if player_input.type == PlayerInputType.MOUSE_LEFT_CLICK:
            return self._view.collides(*player_input.get_property('position'))
        return False

    def _handle_max_time_elapsed(self, current_time):
        if self._io_event_count >= len(self._subscriber_queue):
            return

        waiter = self._subscriber_queue[self._io_event_count]
        if current_time >= waiter.waiting_since + self._max_waiting_time_ms:
            self._last_io_event_check_time = current_time
            waiter.on_arrival_callback()
            self._io_event_count += 1
            game_monitor.notify_io_event_count(self._io_event_count)

    def _handle_probabilistic_io_events(self, current_time):
        if current_time < self._last_io_event_check_time + self._min_waiting_time_ms:
            return
        if self._io_event_count >= len(self._subscriber_queue):
            return

        waiter = self._subscriber_queue[self._io_event_count]
        if current_time >= waiter.waiting_since + self._max_waiting_time_ms:
            return

        self._last_io_event_check_time = current_time

        if randint(1, _IO_EVENT_PROBABILITY_DENOMINATOR) != 1:
            return

        new_io_event_count = randint(self._io_event_count + 1, len(self._subscriber_queue))
        for i in range(self._io_event_count, new_io_event_count):
            self._subscriber_queue[i].on_arrival_callback()
        self._io_event_count = new_io_event_count
        game_monitor.notify_io_event_count(self._io_event_count)

    def _update_blink_color(self, current_time):
        if self._io_event_count > 0:
            self._display_blink_color = (
                int(current_time / _BLINKING_INTERVAL_MS) % 2 == 1
            )
        else:
            self._display_blink_color = False

    def _update_io_events_available_since(self, current_time):
        if self._io_event_count > 0 and self._io_events_available_since is None:
            self._io_events_available_since = current_time

    def update(self, current_time, player_inputs):
        self._current_time = current_time

        for player_input in player_inputs:
            if (
                self._check_if_clicked_on(player_input)
                or (
                    player_input.type == PlayerInputType.KEY_UP
                    and player_input.get_property('key') == 'space'
                )
            ):
                self.handle_player_action()

        self._handle_max_time_elapsed(current_time)
        self._handle_probabilistic_io_events(current_time)
        self._update_blink_color(current_time)
        self._update_io_events_available_since(current_time)
