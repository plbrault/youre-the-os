from lib.drawable import Drawable


class PageSlotView(Drawable):
    def __init__(self):
        super().__init__()

    @property
    def width(self):
        return 36

    @property
    def height(self):
        return 32

    def draw(self, surface):
        pass
