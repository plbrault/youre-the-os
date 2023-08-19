from os import path
import pygame

from lib.drawable import Drawable
from lib.ui.fonts import FONT_PRIMARY_LARGE, FONT_SECONDARY_MEDIUM
from lib.ui.color import Color
from lib.ui.fonts import FONT_PRIMARY_XXLARGE, FONT_SECONDARY_MEDIUM


class CustomSettingsDialogView(Drawable):
    def __init__(self, custom_settings_dialog):
        self._custom_settings_dialog = custom_settings_dialog
        super().__init__()

        self._title_text = FONT_PRIMARY_XXLARGE.render(
            'Custom Settings', True, Color.WHITE)
        self._num_cpus_label_text = FONT_SECONDARY_MEDIUM.render(
            '# CPUs', True, Color.WHITE)
        self._num_processes_label_text = FONT_SECONDARY_MEDIUM.render(
            '# Processes at startup', True, Color.WHITE)
        self._num_ram_rows_label_text = FONT_SECONDARY_MEDIUM.render(
            '# RAM Rows', True, Color.WHITE)
        self._new_process_probability_label_text = FONT_SECONDARY_MEDIUM.render(
            'New Process Probability', True, Color.WHITE)
        self._io_probability_label_text = FONT_SECONDARY_MEDIUM.render(
            'I/O Probability', True, Color.WHITE)

    @property
    def width(self):
        return 520

    @property
    def height(self):
        return 460

    @property
    def label_height(self):
        return self._num_cpus_label_text.get_height()

    @property
    def num_cpus_y(self):
        return self.y + self._title_text.get_height() + 60

    @property
    def num_processes_y(self):
        return self.num_cpus_y + self.label_height + 30

    @property
    def num_ram_rows_y(self):
        return self.num_processes_y + self.label_height + 30

    @property
    def new_process_probability_y(self):
        return self.num_ram_rows_y + self.label_height + 30

    @property
    def io_probability_y(self):
        return self.new_process_probability_y + self.label_height + 30

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(
            self.x, self.y, self.width, self.height), border_radius=3)
        pygame.draw.rect(surface, (70, 70, 70), pygame.Rect(
            self.x + 2, self.y + 2, self.width - 4, self.height - 4), border_radius=3)

        surface.blit(self._title_text, (self.x + (self.width -
                     self._title_text.get_width()) / 2, self.y + 20))
        surface.blit(self._num_cpus_label_text, (self.x + 20, self.num_cpus_y))
        surface.blit(self._num_processes_label_text,
                     (self.x + 20, self.num_processes_y))
        surface.blit(self._num_ram_rows_label_text,
                     (self.x + 20, self.num_ram_rows_y))
        surface.blit(self._new_process_probability_label_text,
                     (self.x + 20, self.new_process_probability_y))
        surface.blit(self._io_probability_label_text,
                     (self.x + 20, self.io_probability_y))
