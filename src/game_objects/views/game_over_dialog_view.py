import pygame

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_20, FONT_ARIAL_10

class GameOverDialogView(Drawable):
    def __init__(self, game_over_dialog):
        super().__init__()

    @property
    def width(self):
        return 800

    @property
    def height(self):
        return 700

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self._x, self._y, self.width, self.height))
