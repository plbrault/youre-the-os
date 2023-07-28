from os import path
import pygame

from lib.drawable import Drawable
from lib.ui.fonts import FONT_PRIMARY_XXLARGE

class MainMenuTitleView(Drawable):
    def __init__(self, main_menu_title):
        self._main_menu_title = main_menu_title
        super().__init__()
        
        original_size_icon = pygame.image.load(path.join('assets', 'icon.png'))
        self._icon = pygame.transform.scale(original_size_icon, (200, 200))
        
        self._text = FONT_PRIMARY_XXLARGE.render("YOU'RE THE OS!", True, (61, 154, 226))

    @property
    def width(self):
        return 1024

    @property
    def height(self):
        return self._icon.get_height() + self._text.get_height() + 20

    def draw(self, surface):
        surface.blit(self._icon, (self.x + (self.width - self._icon.get_width()) / 2, self.y))
        surface.blit(self._text, (self.x + (self.width - self._text.get_width()) / 2, self.y + self._icon.get_height() + 20))
