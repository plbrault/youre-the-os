from ui.color import Color

_LIGHT_COLORS = (
    Color.GREEN,
    Color.YELLOW,
    Color.ORANGE,
    Color.LIGHT_BLUE,
    Color.LIGHT_GREY,
    Color.WHITE,
)


def contrasted_color(color):
    if color in _LIGHT_COLORS:
        return Color.BLACK
    return Color.WHITE
