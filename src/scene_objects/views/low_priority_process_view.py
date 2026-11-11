from os import path
import pygame

from scene_objects.views.process_view import ProcessView

_icon = pygame.image.load(path.join('assets', 'pawn_emoji.png'))

class LowPriorityProcessView(ProcessView):
    def draw(self, surface):
        super().draw(surface)
        surface.blit(_icon, (self._x + 2, self._y + 34))
