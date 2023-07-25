from lib.drawable import Drawable
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_20

class UptimeManagerView(Drawable):
    def __init__(self, uptime_manager):
        self._uptime_manager = uptime_manager
        super().__init__()

    @property
    def width(self):
        return FONT_ARIAL_20.size('Uptime : ' + self._uptime_manager.uptime_text)[0]

    @property
    def height(self):
        return FONT_ARIAL_20.size('Uptime : ' + self._uptime_manager.uptime_text)[1]

    def draw(self, surface):
        surface.blit(FONT_ARIAL_20.render('Uptime : ' + self._uptime_manager.uptime_text, False, Color.WHITE), (512 - self.width / 2, 10))
