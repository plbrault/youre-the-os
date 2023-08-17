from os import path
import pygame

from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_XXLARGE, FONT_SECONDARY_SMALL, FONT_SECONDARY_XSMALL, FONT_SECONDARY_XXSMALL

class KeyBindingDialogView(Drawable):
    def __init__(self, about_dialog):
        self.about_dialog = about_dialog
        super().__init__()
        
        self._title_text = FONT_PRIMARY_XXLARGE.render('Key Bindings', True, Color.WHITE)
        
        self._explanation_text_row_1 = FONT_SECONDARY_SMALL.render('You can use the following key bindings to do the', True, Color.WHITE)
        self._explanation_text_row_2 = FONT_SECONDARY_SMALL.render('same actions that can be performed with the mouse:', True, Color.WHITE)
        
    @property
    def width(self):
        return 540

    @property
    def height(self):
        return 460

    def draw(self, surface):
        y = self.y + 40
        
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(self.x, self.y, self.width, self.height), border_radius=3)
        pygame.draw.rect(surface, (70, 70, 70), pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4), border_radius=3)
        
        surface.blit(self._title_text, (self.x + (self.width - self._title_text.get_width()) / 2, self.y + 30))
        
        y += self._title_text.get_height() + 20
        surface.blit(self._explanation_text_row_1, (self.x + (self.width - self._explanation_text_row_1.get_width()) / 2, y))
        
        y += self._explanation_text_row_1.get_height() + 2     
        surface.blit(self._explanation_text_row_2, (self.x + (self.width - self._explanation_text_row_2.get_width()) / 2, y))
        

