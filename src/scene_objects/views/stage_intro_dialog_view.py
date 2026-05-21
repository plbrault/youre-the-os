from engine.modal_view import ModalView
from ui.color import Color
from ui.fonts import FONT_PRIMARY_XLARGE, FONT_PRIMARY_LARGE, FONT_PRIMARY_MEDIUM


class StageIntroDialogView(ModalView):
    WIDTH = 480
    PADDING = 30
    HEADING_SPACING = 24
    ITEM_SPACING = 4
    SECTION_SPACING = 16
    BUTTON_BOTTOM_MARGIN = 40

    def __init__(self, dialog):
        self._dialog = dialog
        super().__init__()
        self._title_surface = FONT_PRIMARY_XLARGE.render(
            self._dialog.title, True, Color.WHITE)
        self._section_headings = []
        self._section_items = []
        for section in self._dialog.sections:
            heading_surface = FONT_PRIMARY_LARGE.render(
                section.heading, True, Color.WHITE)
            self._section_headings.append(heading_surface)
            items = []
            for item in section.items:
                item_surface = FONT_PRIMARY_MEDIUM.render(
                    '\u2022 ' + item, True, Color.WHITE)
                items.append(item_surface)
            self._section_items.append(items)

    @ModalView.x.setter
    def x(self, value):
        self._x = value
        self._dialog.start_button.view.x = (
            self.x + (self.width - self._dialog.start_button.view.width) / 2)

    @ModalView.y.setter
    def y(self, value):
        self._y = value
        self._dialog.start_button.view.y = (
            self.y + self.height - self._dialog.start_button.view.height
            - self.BUTTON_BOTTOM_MARGIN)

    @property
    def width(self):
        return self.WIDTH

    @property
    def height(self):
        y = self.PADDING
        y += self._title_surface.get_height() + self.HEADING_SPACING
        for i, heading_surface in enumerate(self._section_headings):
            y += heading_surface.get_height() + self.ITEM_SPACING
            for item_surface in self._section_items[i]:
                y += item_surface.get_height() + self.ITEM_SPACING
            y += self.SECTION_SPACING
        y += self.BUTTON_BOTTOM_MARGIN
        y += self._dialog.start_button.view.height
        y += self.BUTTON_BOTTOM_MARGIN
        return y

    def draw_content(self, surface):
        x = self.x + self.PADDING
        y = self.y + self.PADDING

        surface.blit(self._title_surface, (
            self.x + (self.width - self._title_surface.get_width()) / 2, y))
        y += self._title_surface.get_height() + self.HEADING_SPACING

        for i, heading_surface in enumerate(self._section_headings):
            surface.blit(heading_surface, (x, y))
            y += heading_surface.get_height() + self.ITEM_SPACING
            for item_surface in self._section_items[i]:
                surface.blit(item_surface, (x + self.ITEM_SPACING * 4, y))
                y += item_surface.get_height() + self.ITEM_SPACING
            y += self.SECTION_SPACING
