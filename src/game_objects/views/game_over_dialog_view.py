from os import path
import pygame

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_LARGE, FONT_PRIMARY_XLARGE, FONT_PRIMARY_XXLARGE

class GameOverDialogView(Drawable):
    def __init__(self, game_over_dialog):
        super().__init__()
        
        self._image = pygame.image.load(path.join('assets', 'shutdown.jpg'))
        
        self._main_text_surface = FONT_PRIMARY_XXLARGE.render('YOU GOT REBOOTED!', False, Color.WHITE)
        self._uptime_text_surface = FONT_PRIMARY_LARGE.render('UPTIME: ' + game_over_dialog.uptime, False, Color.WHITE)
        self._score_text_surface = FONT_PRIMARY_LARGE.render('SCORE: ' + str(game_over_dialog.score), False, Color.WHITE)

    @property
    def width(self):
        return self._image.get_width() + 4

    @property
    def height(self):
        return 680

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self.x, self.y, self.width, self.height), border_radius=3)
        pygame.draw.rect(surface, (70, 70, 70), pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4), border_radius=3)

        surface.blit(self._main_text_surface, (self.x + (self.width - self._main_text_surface.get_width()) / 2, self.y + 20))
        
        surface.blit(self._image, (self._x + 2, self._y + self._main_text_surface.get_height() + 40))
        
        surface.blit(self._uptime_text_surface, (
            self.x + 20,
            self.y + self._main_text_surface.get_height() + self._image.get_height() + 80
        ))
        surface.blit(self._score_text_surface, (
            self.x + self.width - self._score_text_surface.get_width() - 20,
            self.y + self._main_text_surface.get_height() + self._image.get_height() + 80
        ))        
