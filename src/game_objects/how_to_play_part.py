from lib.game_object import GameObject
from game_objects.button import Button
from game_objects.views.how_to_play_part_view import HowToPlayPartView

class HowToPlayPart(GameObject):
    
    def __init__(self, text, image_file_paths):
        self._text = text
        self._image_file_paths = image_file_paths
        super().__init__(HowToPlayPartView(self))

    @property
    def text(self):
        return self._text
    
    @property
    def image_file_paths(self):
        return self._image_file_paths

    def update(self, current_time, events):
        for child in self.children:
            child.update(current_time, events)
    