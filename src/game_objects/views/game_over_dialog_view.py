import pygame
import os

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_20, FONT_ARIAL_10

class GameOverDialogView(Drawable):
    def __init__(self, game_over_dialog):
        super().__init__()
        self._image = pygame.image.load(os.path.join('assets', 'game-over-image.png')).convert_alpha()

    @property
    def width(self):
        return 700

    @property
    def height(self):
        return 700

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self._x, self._y, self.width, self.height))
        surface.blit(self._image, (self._x + 30, self._y + 104))
