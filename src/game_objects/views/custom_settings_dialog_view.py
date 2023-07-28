from os import path
import pygame

from lib.drawable import Drawable
from lib.ui.fonts import FONT_PRIMARY_LARGE, FONT_SECONDARY_MEDIUM
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_XXLARGE, FONT_SECONDARY_MEDIUM

class CustomSettingsDialogView(Drawable):
    def __init__(self, custom_settings_dialog):
        self._custom_settings_dialog = custom_settings_dialog
        super().__init__()
        
        self._title_text = FONT_PRIMARY_XXLARGE.render('Custom Settings', True, Color.WHITE)
        self._num_cpus_label_text = FONT_SECONDARY_MEDIUM.render('Number of CPUs', True, Color.WHITE)
        
    @property
    def width(self):
        return 400

    @property
    def height(self):
        return 400
    
    @property
    def num_cpus_y(self):
        return self.y + self._title_text.get_height() + 40
    
    @property
    def num_cpus_height(self):
        return self._num_cpus_label_text.get_height()

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self.x, self.y, self.width, self.height), border_radius=3)
        pygame.draw.rect(surface, (70, 70, 70), pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4), border_radius=3)
        
        surface.blit(self._title_text, (self.x + (self.height - self._title_text.get_width()) / 2, self.y + 10))
        surface.blit(self._num_cpus_label_text, (self.x + 10, self.num_cpus_y))
