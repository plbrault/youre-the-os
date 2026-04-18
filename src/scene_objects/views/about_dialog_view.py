from game_info import TITLE, VERSION, COPYRIGHT_YEAR
from engine.modal_view import ModalView
from ui.color import Color
from ui.fonts import FONT_PRIMARY_XXLARGE, FONT_SECONDARY_SMALL, FONT_SECONDARY_XSMALL


class AboutDialogView(ModalView):
    def __init__(self, about_dialog):
        self.about_dialog = about_dialog
        super().__init__()

    @ModalView.x.setter
    def x(self, value):
        self._x = value
        self.about_dialog.close_button.view.x = self.x + (
            self.width - self.about_dialog.close_button.view.width) / 2

    @ModalView.y.setter
    def y(self, value):
        self._y = value
        self.about_dialog.close_button.view.y = (
            self.y + self.height - self.about_dialog.close_button.view.height - 40)

        self._title_text = FONT_PRIMARY_XXLARGE.render(
            TITLE, True, Color.WHITE)
        self._version_text = FONT_SECONDARY_SMALL.render(
            'Version ' + VERSION, True, Color.WHITE)
        self._copyright_text = FONT_SECONDARY_SMALL.render(
            '© ' + COPYRIGHT_YEAR + ' Pier-Luc Brault', True, Color.WHITE)
        self._license_text = FONT_SECONDARY_XSMALL.render(
            'This game is published under the GNU General Public License Version 3.',
            True,
            Color.WHITE)
        self._license_url_text = FONT_SECONDARY_XSMALL.render(
            '<https://www.gnu.org/licenses/gpl-3.0.html>', True, Color.WHITE)
        self._asset_credits_title = FONT_SECONDARY_XSMALL.render(
            'Asset Credits and Licenses:', True, Color.WHITE)
        self._asset_credits = [
            FONT_SECONDARY_XSMALL.render(
                'Game icon/logo: original image by Muhammat Sukirman (CC BY 3.0).',
                True,
                Color.WHITE),
            FONT_SECONDARY_XSMALL.render(
                'Primary font: VT323 by Peter Hull (SIL Open Font License).',
                True,
                Color.WHITE),
            FONT_SECONDARY_XSMALL.render(
                'Secondary font: Victor Mono by Rune Bjørnerås (SIL Open Font License).',
                True,
                Color.WHITE),
            FONT_SECONDARY_XSMALL.render(
                'All emojis are from OpenMoji.org (CC BY-SA 4.0).',
                True,
                Color.WHITE),
            FONT_SECONDARY_XSMALL.render(
                'Image in the "YOU GOT REBOOTED!" dialog is by Aleksandar Cvetanović (CC0).',
                True,
                Color.WHITE),
        ]

    @property
    def width(self):
        return 540

    @property
    def height(self):
        return 540

    def draw_content(self, surface):
        y = self.y + 40

        surface.blit(self._title_text, (self.x + (self.width -
                     self._title_text.get_width()) / 2, self.y + 30))

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
        surface.blit(self._asset_credits_title, (
            self.x + (self.width - self._asset_credits_title.get_width()) / 2,
            y
        ))

        y += self._asset_credits_title.get_height() + 10
        for text in self._asset_credits:
            surface.blit(text, (
                self.x + (self.width - text.get_width()) / 2,
                y
            ))
            y += text.get_height() + 5
