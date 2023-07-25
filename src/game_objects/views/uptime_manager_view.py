from lib.drawable import Drawable

class UptimeManagerView(Drawable):
    def __init__(self, uptime_manager):
        self._uptime_manager = uptime_manager
        super().__init__()

    @property
    def width(self):
        return 0

    @property
    def height(self):
        return 0

    def draw(self, surface):
        pass
