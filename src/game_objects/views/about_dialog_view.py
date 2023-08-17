from os import path
import pygame

from game_info import TITLE, VERSION, COPYRIGHT_YEAR
from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_XXLARGE, FONT_SECONDARY_SMALL, FONT_SECONDARY_XSMALL, FONT_SECONDARY_XXSMALL

class AboutDialogView(Drawable):
    def __init__(self, about_dialog):
        self.about_dialog = about_dialog
        super().__init__()
        
        self._title_text = FONT_PRIMARY_XXLARGE.render(TITLE, True, Color.WHITE)
        self._version_text = FONT_SECONDARY_SMALL.render('Version ' + VERSION, True, Color.WHITE)
        self._copyright_text = FONT_SECONDARY_SMALL.render('© ' + COPYRIGHT_YEAR + ' Pier-Luc Brault', True, Color.WHITE)
        self._license_text = FONT_SECONDARY_XSMALL.render('This game is published under the GNU General Public License Version 3.', True, Color.WHITE)
        self._license_url_text = FONT_SECONDARY_XSMALL.render('<https://www.gnu.org/licenses/gpl-3.0.html>', True, Color.WHITE)
        self._asset_license_text = FONT_SECONDARY_XSMALL.render('Game assets are published under their own licenses.', True, Color.WHITE)
        self._asset_license_details_text = FONT_SECONDARY_XSMALL.render('See <https://github.com/plbrault/youre-the-os> for details.', True, Color.WHITE)
        
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
        surface.blit(self._version_text, (
            self.x + (self.width - self._version_text.get_width()) / 2,
            y
        ))
        
        y += self._version_text.get_height() + 20
        surface.blit(self._copyright_text, (
            self.x + (self.width - self._copyright_text.get_width()) / 2,
            y
        ))
        
        y += self._copyright_text.get_height() + 40
        surface.blit(self._license_text, (
            self.x + (self.width - self._license_text.get_width()) / 2,
            y
        ))
        
        y += self._license_text.get_height() + 10
        surface.blit(self._license_url_text, (
            self.x + (self.width - self._license_url_text.get_width()) / 2,
            y
        ))
        
        y += self._license_url_text.get_height() + 40
        surface.blit(self._asset_license_text, (
            self.x + (self.width - self._asset_license_text.get_width()) / 2,
            y
        ))
        
        y += self._asset_license_text.get_height() + 10
        surface.blit(self._asset_license_details_text, (
            self.x + (self.width - self._asset_license_details_text.get_width()) / 2,
            y
        ))                           
