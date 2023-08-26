from queue import SimpleQueue
from random import randint

from lib import event_manager
from lib.game_object import GameObject
from lib.game_event_type import GameEventType
from game_objects.views.io_queue_view import IoQueueView


class IoQueue(GameObject):

    def __init__(self):
        self._subscriber_queue = SimpleQueue()
        self._event_count = 0
        self._last_update_time = 0

        super().__init__(IoQueueView(self))

    def wait_for_event(self, callback):
        self._subscriber_queue.put(callback)

    @property
    def event_count(self):
        return self._event_count

    def process_events(self):
        while self.event_count > 0:
            self._event_count -= 1
            callback = self._subscriber_queue.get()
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

        if current_time >= self._last_update_time + 1000:
            self._last_update_time = current_time

            if self._event_count < self._subscriber_queue.qsize() and randint(1, 3) == 3:
                self._event_count = randint(
                    self._event_count + 1, self._subscriber_queue.qsize())
                event_manager.event_io_queue(self._event_count)
