from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_SECONDARY_MEDIUM


class DifficultySelectionLabelView(Drawable):
    def __init__(self, difficulty_selection_label):
        self._difficulty_selection_label = difficulty_selection_label
        super().__init__()

        self._text = FONT_SECONDARY_MEDIUM.render(
            "Select Difficulty:", True, Color.WHITE)

    @property
    def width(self):
        return self._text.get_width()

    @property
    def height(self):
        return self._text.get_height()

    def draw(self, surface):
        surface.blit(self._text, (self.x, self.y))
