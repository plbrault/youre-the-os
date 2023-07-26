from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_20

class ProcessManagerView(Drawable):
    def __init__(self, process_manager):
        self._process_manager = process_manager
        super().__init__()
        
        self._idle_processes_text_surface = FONT_ARIAL_20.render('Idle Processes :', False, Color.WHITE)
        self._terminated_processes_text_surface = FONT_ARIAL_20.render('User Ragequits :', False, Color.WHITE)

    @property
    def width(self):
        return 530

    @property
    def height(self):
        return 768

    def draw(self, surface):
        surface.blit(self._idle_processes_text_surface, (50, 120))
        surface.blit(self._terminated_processes_text_surface, (50, 668))
