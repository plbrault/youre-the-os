from lib.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_SECONDARY_MEDIUM


class OptionSelectorView(Drawable):
    def __init__(self, option_selector):
        self._option_selector = option_selector
        super().__init__()

        self._min_width = 0

        self._option_surfaces = []
        longest_option_id = 0
        for i, option in enumerate(self._option_selector.options):
            self._option_surfaces.append(FONT_SECONDARY_MEDIUM.render(
                option.upper(), False, Color.WHITE))
            if len(option) > len(
                    self._option_selector.options[longest_option_id]):
                longest_option_id = i

        self._max_text_width = self._option_surfaces[longest_option_id].get_width(
        )
        self._text_height = self._option_surfaces[longest_option_id].get_height(
        )

    @property
    def min_width(self):
        return self._min_width

    @min_width.setter
    def min_width(self, value):
        self._min_width = value

    @property
    def width(self):
        return max(
            self.min_width,
            self._max_text_width +
            self._option_selector.previous_button.view.width +
            self._option_selector.next_button.view.width +
            40)

    @property
    def height(self):
        return max(self._text_height,
                   self._option_selector.previous_button.view.height)

    def draw(self, surface):
        text_surface = self._option_surfaces[self._option_selector.selected_option_id]
        surface.blit(text_surface, (
            self.x + (self.width - text_surface.get_width()) / 2,
            self.y + (self.height - text_surface.get_height()) / 2
        ))
