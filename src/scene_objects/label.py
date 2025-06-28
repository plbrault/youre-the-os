from engine.scene_object import SceneObject
from scene_objects.views.label_view import LabelView


class Label(SceneObject):
    def __init__(self, text):
        super().__init__(LabelView(self))
        self._text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self._view.update()
