import pygame
import os

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_16, FONT_ARIAL_30
from game_objects.label import Label

class GameOverDialogView(Drawable):
    def __init__(self, game_over_dialog):
        super().__init__()
        
        self._image = pygame.image.load(os.path.join('assets', 'game-over-image.png')).convert_alpha()
        
        self._game_over_label = Label('GAME OVER')
        self._game_over_label.font = FONT_ARIAL_30
        self._game_over_label.color = Color.WHITE

        self._explanation_label = Label('You made the user angry!')
        self._explanation_label.font = FONT_ARIAL_16
        self._explanation_label.color = Color.WHITE

    @property
    def width(self):
        return 700

    @property
    def height(self):
        return 700

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self.x, self.y, self.width, self.height), border_radius=3)
        pygame.draw.rect(surface, Color.ALMOST_BLACK, pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4), border_radius=3)
        surface.blit(self._image, (self._x + 30, self._y + 98))

        self._game_over_label.view.setXY((self.width - self._game_over_label.view.width) / 2 + self.x, self.y + 20)
        self._game_over_label.render(surface)

        self._explanation_label.view.setXY(
            (self.width - self._explanation_label.view.width) / 2 + self.x,
            self._game_over_label.view.y + self._game_over_label.view.height + 5,
        )
        self._explanation_label.render(surface)
