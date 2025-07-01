from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_PRIMARY_LARGE
from scene_objects.views.process_view import ProcessView
from window_size import WINDOW_WIDTH, WINDOW_HEIGHT


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
