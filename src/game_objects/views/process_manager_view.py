from lib.drawable import Drawable

class ProcessManagerView(Drawable):
    def __init__(self, process_manager):
        self._process_manager = process_manager
        super().__init__()

    @property
    def width(self):
        return 530

    @property
    def height(self):
        return 768

    def draw(self, surface):
        pass
