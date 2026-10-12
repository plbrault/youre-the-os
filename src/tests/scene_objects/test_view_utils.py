from scene_objects.views.view_utils import contrasted_color
from ui.color import Color


class TestContrastedColor:
    def test_returns_black_for_light_colors(self):
        light_colors = [
            Color.GREEN,
            Color.YELLOW,
            Color.ORANGE,
            Color.LIGHT_BLUE,
            Color.LIGHT_GREY,
            Color.WHITE,
        ]

        for color in light_colors:
            assert contrasted_color(color) == Color.BLACK

    def test_returns_white_for_dark_colors(self):
        dark_colors = [
            Color.BLACK,
            Color.DARK_GREY,
            Color.DARK_RED,
            Color.DARKER_RED,
            Color.RED,
            Color.BLUE,
            Color.TEAL,
        ]

        for color in dark_colors:
            assert contrasted_color(color) == Color.WHITE
