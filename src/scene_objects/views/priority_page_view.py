from os import path
import pygame

from scene_objects.views.page_view import PageView

_CROWN_ICON_SIZE = 12
_icon = pygame.image.load(path.join('assets', 'crown_emoji.png'))
_crown = pygame.transform.scale(_icon, (_CROWN_ICON_SIZE, _CROWN_ICON_SIZE))

class PriorityPageView(PageView):
    def draw(self, surface):
        super().draw(surface)
        surface.blit(
            _crown,
            (self._x + self.width - _CROWN_ICON_SIZE - 1,
             self._y + self.height - _CROWN_ICON_SIZE - 5))
