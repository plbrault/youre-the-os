from queue import SimpleQueue
from random import randint

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

    def _checkIfClickedOn(self, event):
        if event.type == GameEventType.MOUSE_LEFT_CLICK:
            return self._view.collides(*event.getProperty('position'))
        return False

    def _onClick(self):
        while self.event_count > 0:
            self._event_count -= 1
            callback = self._subscriber_queue.get()
            callback()

    def update(self, current_time, events):
        for event in events:
            if event.type == GameEventType.KEY_PRESS:
                if event.getProperty('key') == 'CTRL':
                    self._onClick()
            elif self._checkIfClickedOn(event):
                self._onClick()

        if current_time >= self._last_update_time + 1000:
            self._last_update_time = current_time

            if self._event_count < self._subscriber_queue.qsize() and randint(1, 3) == 3:
                self._event_count = randint(self._event_count + 1, self._subscriber_queue.qsize())
