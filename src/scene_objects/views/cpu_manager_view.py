from engine.drawable import Drawable


class CpuManagerView(Drawable):
    def __init__(self, cpu_manager):
        self.cpu_manager = cpu_manager
        super().__init__()

    @property
    def width(self):
        return 0

    @property
    def height(self):
        return 0

    def draw(self, surface):
        pass
