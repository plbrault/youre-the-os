import pygame
import os

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_12, FONT_PRIMARY_18, FONT_PRIMARY_30

class GameOverDialogView(Drawable):
    def __init__(self, game_over_dialog):
        super().__init__()
        
        self._image = pygame.image.load(os.path.join('assets', 'game-over-image.png')).convert_alpha()
        
        self._main_text_surface = FONT_PRIMARY_30.render('GAME OVER', False, Color.WHITE)
        self._secondary_text_surface = FONT_PRIMARY_18.render('You made the user angry!', False, Color.WHITE)
        self._press_any_key_text_surface = FONT_PRIMARY_12.render('Press any key to try again', False, Color.WHITE)

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

        surface.blit(self._main_text_surface, (self.x + (self.width - self._main_text_surface.get_width()) / 2, self.y + 20))
        surface.blit(self._secondary_text_surface, (
            self.x + (self.width - self._secondary_text_surface.get_width()) / 2,
            self.y + self._main_text_surface.get_height() + 25
        ))
        surface.blit(self._press_any_key_text_surface, (
            self.x + (self.width - self._press_any_key_text_surface.get_width()) / 2,
            self.y + self._main_text_surface.get_height() + self._secondary_text_surface.get_height() + 50
        ))
