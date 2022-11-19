from lib.game_object import GameObject
from game_objects.views.label_view import LabelView

class Label(GameObject):
    def __init__(self, text = ''):
        self._text = text

        super().__init__(LabelView(self))

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = str(text)

    @property
    def font(self):
        return self.view.font

    @font.setter
    def font(self, font):
        self.view.font = font

    @property
    def color(self):
        return self.view.color

    @color.setter
    def color(self, color):
        self.view.color = color

    def update(self, current_time, events):
        pass
    