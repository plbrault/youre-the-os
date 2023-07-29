from lib.game_object import GameObject
from game_objects.button import Button
from game_objects.views.how_to_play_part_1_view import HowToPlayPart1View

class HowToPlayPart1(GameObject):
    
    def __init__(self):
        super().__init__(HowToPlayPart1View(self))

    def update(self, current_time, events):
        for child in self.children:
            child.update(current_time, events)
    