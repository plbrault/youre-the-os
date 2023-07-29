from difficulty_levels import default_difficulty
from lib.game_object import GameObject
from game_objects.button import Button
from game_objects.option_selector import OptionSelector
from game_objects.views.about_dialog_view import AboutDialogView

class AboutDialog(GameObject):
    
    def __init__(self):
        super().__init__(AboutDialogView(self))

    def update(self, current_time, events):       
        for child in self.children:
            child.update(current_time, events)
    