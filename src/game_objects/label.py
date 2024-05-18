from engine.game_object import GameObject
from game_objects.views.label_view import LabelView


class Label(GameObject):
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
