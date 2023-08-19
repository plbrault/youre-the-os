from lib.game_object import GameObject
from game_objects.views.how_to_play_part_view import HowToPlayPartView


class HowToPlayPart(GameObject):

    def __init__(self, text, images, animation_interval=1000):
        self._text = text
        self._images = images
        self._animation_interval = animation_interval
        super().__init__(HowToPlayPartView(self))

        self._initial_time = 0
        self._current_image_id = 0

    @property
    def text(self):
        return self._text

    @property
    def images(self):
        return self._images

    @property
    def initial_time(self):
        return self._initial_time

    @initial_time.setter
    def initial_time(self, initial_time):
        self._initial_time = initial_time

    @property
    def current_image_id(self):
        return self._current_image_id

    def update(self, current_time, events):
        self._current_image_id = int(
            (current_time - self.initial_time) / self._animation_interval) % len(self._images)

        for child in self.children:
            child.update(current_time, events)
