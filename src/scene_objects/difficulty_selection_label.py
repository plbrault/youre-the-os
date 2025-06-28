from engine.scene_object import SceneObject
from scene_objects.views.difficulty_selection_label_view import DifficultySelectionLabelView


class DifficultySelectionLabel(SceneObject):

    def __init__(self):
        super().__init__(DifficultySelectionLabelView(self))
