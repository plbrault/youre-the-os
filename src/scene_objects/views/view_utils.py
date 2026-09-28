from ui.color import Color


class ViewUtils:
    def contrasted_color(self, color):
        match color:
            case Color.GREEN | Color.YELLOW | Color.ORANGE | Color.LIGHT_BLUE | Color.LIGHT_GREY | Color.WHITE:
                return Color.BLACK
            case _:
                return Color.WHITE
