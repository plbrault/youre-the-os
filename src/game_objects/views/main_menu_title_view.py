import pygame

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_MEDIUM

class MainMenuTitleView(Drawable):
    def __init__(self, main_menu_title):
        self._main_menu_title = main_menu_title
        super().__init__()

    @property
    def width(self):
        return 0

    @property
    def height(self):
        return 0

    def draw(self, surface):
        pass
