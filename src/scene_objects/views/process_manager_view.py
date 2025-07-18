from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_PRIMARY_LARGE
from scene_objects.views.process_view import ProcessView
from window_size import WINDOW_WIDTH, WINDOW_HEIGHT


class ProcessManagerView(Drawable):
    def __init__(self, process_manager):
        self._process_manager = process_manager
        super().__init__()

        self._idle_processes_text_surface = FONT_PRIMARY_LARGE.render(
            'Idle Processes :', False, Color.WHITE)
        self._process_view_height = ProcessView.height

    @property
    def width(self):
        return WINDOW_WIDTH - self._process_manager.view_vars['page_manager_view_width']

    @property
    def height(self):
        return WINDOW_HEIGHT

    def draw(self, surface):
        terminated_processes_text = f'User Ragequits ({self._process_manager.user_terminated_process_count} / {self._process_manager.max_processes_terminated_by_user}) :' # pylint: disable=line-too-long

        terminated_processes_text_surface = FONT_PRIMARY_LARGE.render(
            terminated_processes_text, False, Color.WHITE)

        surface.blit(self._idle_processes_text_surface, (50, 120))
        surface.blit(terminated_processes_text_surface, (
            50,
            WINDOW_HEIGHT - self._process_view_height -
            terminated_processes_text_surface.get_height() - 30
        ))
