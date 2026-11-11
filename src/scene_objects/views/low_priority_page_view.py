from os import path
import pygame

from scene_objects.views.page_view import PageView

_PAWN_ICON_SIZE = 12
_icon = pygame.image.load(path.join('assets', 'pawn_emoji.png'))
_pawn = pygame.transform.scale(_icon, (_PAWN_ICON_SIZE, _PAWN_ICON_SIZE))

class LowPriorityPageView(PageView):
    def draw(self, surface):
        super().draw(surface)
        surface.blit(
            _pawn,
            (self._x + self.width - _PAWN_ICON_SIZE - 1,
             self._y + self.height - _PAWN_ICON_SIZE - 5))
