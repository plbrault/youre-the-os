from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_18

class ProcessManagerView(Drawable):
    def __init__(self, process_manager):
        self._process_manager = process_manager
        super().__init__()
        
        self._idle_processes_text_surface = FONT_PRIMARY_18.render('Idle Processes :', False, Color.WHITE)

    @property
    def width(self):
        return 530

    @property
    def height(self):
        return 768

    def draw(self, surface):
        terminated_processes_text = 'User Ragequits ({0} / {1}) :'.format(
            self._process_manager.user_terminated_process_count,
            self._process_manager.MAX_TERMINATED_BY_USER
        )
        
        terminated_processes_text_surface = FONT_PRIMARY_18.render(terminated_processes_text, False, Color.WHITE)
        
        surface.blit(self._idle_processes_text_surface, (50, 120))
        surface.blit(terminated_processes_text_surface, (50, 658))
