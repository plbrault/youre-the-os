import pygame

from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_SECONDARY_XXXSMALL


class PageView(Drawable):
    def __init__(self, page):
        self._page = page
        self._pid_text_surface = FONT_SECONDARY_XXXSMALL.render(
            'PID ' + str(self._page.pid), False, Color.BLACK)
        super().__init__()

    @property
    def width(self):
        return 36

    @property
    def height(self):
        return 32

    def draw(self, surface):
        color = Color.DARK_GREY
        if self._page.swap_in_progress:
            color = Color.TEAL
        elif self._page.display_blink_color:
            color = Color.BLUE
        elif self._page.in_use:
            color = Color.WHITE
        pygame.draw.rect(surface, color, pygame.Rect(
            self._x, self._y, self.width, self.height))
        surface.blit(self._pid_text_surface, (self._x + 1, self._y + 5))

        if self._page.swap_in_progress:
            progress_bar_width = (self.width - 4) * self._page.swap_percentage_completed
            progress_bar_height = 2
            pygame.draw.rect(surface, Color.BLACK, pygame.Rect(
                self._x + 2,
                self._y + self.height - 4,
                progress_bar_width,
                progress_bar_height
            ))
