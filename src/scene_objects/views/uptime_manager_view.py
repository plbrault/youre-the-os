from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_PRIMARY_MEDIUM


class UptimeManagerView(Drawable):
    def __init__(self, uptime_manager):
        self._uptime_manager = uptime_manager
        super().__init__()

    @property
    def width(self):
        return FONT_PRIMARY_MEDIUM.size(
            'Uptime : ' + self._uptime_manager.uptime_text)[0]

    @property
    def height(self):
        return FONT_PRIMARY_MEDIUM.size(
            'Uptime : ' + self._uptime_manager.uptime_text)[1]

    def draw(self, surface):
        surface.blit(
            FONT_PRIMARY_MEDIUM.render(
                'Uptime : ' +
                self._uptime_manager.uptime_text,
                False,
                Color.WHITE),
            (self.x, self.y))
