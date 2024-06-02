from os import path
import pygame

from game_objects.views.process_view import ProcessView

_icon = pygame.image.load(path.join('assets', 'crown_emoji.png'))

class PriorityProcessView(ProcessView):
    def __init__(self, process):
        super().__init__(process)

    def draw(self, surface):
        super().draw(surface)
        surface.blit(_icon, (self._x + 2, self._y + 34))