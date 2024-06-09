from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_PRIMARY_MEDIUM


class ScoreManagerView(Drawable):
    def __init__(self, score_manager):
        self._score_manager = score_manager
        super().__init__()

    @property
    def width(self):
        return FONT_PRIMARY_MEDIUM.size(
            'Score: ' + format(self._score_manager.score, '09'))[0]

    @property
    def height(self):
        return FONT_PRIMARY_MEDIUM.size(
            'Score: ' + format(self._score_manager.score, '09'))[1]

    def draw(self, surface):
        surface.blit(
            FONT_PRIMARY_MEDIUM.render(
                'Score: ' +
                format(
                    self._score_manager.score,
                    '09'),
                False,
                Color.WHITE),
            (self.x, self.y))
