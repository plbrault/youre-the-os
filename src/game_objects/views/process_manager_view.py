from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_LARGE
from game_objects.process import Process
from game_objects.views.process_view import ProcessView
from window_size import WINDOW_WIDTH, WINDOW_HEIGHT

class ProcessManagerView(Drawable):
    def __init__(self, process_manager):
        self._process_manager = process_manager
        super().__init__()

        self._idle_processes_text_surface = FONT_PRIMARY_LARGE.render('Idle Processes :', False, Color.WHITE)
        self._PROCESS_VIEW_HEIGHT = ProcessView(Process(0, process_manager.game)).height

    @property
    def width(self):
        return WINDOW_WIDTH - self._process_manager.game.page_manager.view.width

    @property
    def height(self):
        return WINDOW_HEIGHT

    def draw(self, surface):
        terminated_processes_text = 'User Ragequits ({0} / {1}) :'.format(
            self._process_manager.user_terminated_process_count,
            self._process_manager.MAX_TERMINATED_BY_USER
        )

        terminated_processes_text_surface = FONT_PRIMARY_LARGE.render(terminated_processes_text, False, Color.WHITE)

        surface.blit(self._idle_processes_text_surface, (50, 120))
        surface.blit(terminated_processes_text_surface, (
            50,
            WINDOW_HEIGHT - self._PROCESS_VIEW_HEIGHT - terminated_processes_text_surface.get_height() - 30
        ))
