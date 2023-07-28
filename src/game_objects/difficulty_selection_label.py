from lib.game_object import GameObject
from game_objects.button import Button
from game_objects.views.difficulty_selection_label_view import DifficultySelectionLabelView

class DifficultySelectionLabel(GameObject):
    
    def __init__(self):
        super().__init__(DifficultySelectionLabelView(self))
    