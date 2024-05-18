from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_PRIMARY_MEDIUM

_font = FONT_PRIMARY_MEDIUM


class LabelView(Drawable):
    def __init__(self, label):
        self._label = label
        super().__init__()

    @property
    def width(self):
        return _font.size(self._label.text)[0]

    @property
    def height(self):
        return _font.size(self._label.text)[1]

    def draw(self, surface):
        surface.blit(_font.render(self._label.text, False, Color.WHITE), (self.x, self.y))
