from lib.game_object import GameObject
from game_objects.button import Button
from game_objects.views.how_to_play_part_view import HowToPlayPartView

class HowToPlayPart(GameObject):
    
    def __init__(self, text, image_file_paths):
        self._text = text
        self._image_file_paths = image_file_paths
        super().__init__(HowToPlayPartView(self))
        
        self._initial_time = 0
        self._current_image_id = 0

    @property
    def text(self):
        return self._text
    
    @property
    def image_file_paths(self):
        return self._image_file_paths
    
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
        self._current_image_id = int((current_time - self.initial_time) / 1000) % len(self._image_file_paths)
        
        for child in self.children:
            child.update(current_time, events)
    