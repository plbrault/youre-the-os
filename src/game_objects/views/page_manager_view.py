from lib.drawable import Drawable

class PageManagerView(Drawable):
    def __init__(self, page_manager):
        self.page_manager = page_manager
        super().__init__()

    @property
    def width(self):
        return 610

    @property
    def height(self):
        return 768

    def draw(self, surface):
        pass
