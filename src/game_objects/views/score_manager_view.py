from lib.drawable import Drawable

class ScoreManagerView(Drawable):
    def __init__(self, score_manager):
        self._score_manager = score_manager
        super().__init__()

    @property
    def width(self):
        return 0

    @property
    def height(self):
        return 0

    def draw(self, surface):
        pass
