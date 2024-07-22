import pygame

from engine.drawable import Drawable
from ui.fonts import FONT_SECONDARY_MEDIUM, FONT_PRIMARY_XXLARGE
from ui.color import Color

class CustomSettingsDialogView(Drawable):
    def __init__(self, custom_settings_dialog):
        self._custom_settings_dialog = custom_settings_dialog
        super().__init__()

        self._title_text = FONT_PRIMARY_XXLARGE.render(
            'Custom Settings', True, Color.WHITE)
        self._num_cpus_label_text = FONT_SECONDARY_MEDIUM.render(
            '# CPUs', True, Color.WHITE)
        self._num_processes_at_startup_label_text = FONT_SECONDARY_MEDIUM.render(
            '# Processes at startup', True, Color.WHITE)
        self._max_processes_label_text = FONT_SECONDARY_MEDIUM.render(
            'Max # Processes', True, Color.WHITE)
        self._num_ram_rows_label_text = FONT_SECONDARY_MEDIUM.render(
            '# RAM Rows', True, Color.WHITE)
        self._swap_delay_label_text = FONT_SECONDARY_MEDIUM.render(
            'Swap Latency', True, Color.WHITE)
        self._new_process_probability_label_text = FONT_SECONDARY_MEDIUM.render(
            'New Process Probability', True, Color.WHITE)
        self._priority_process_probability_label_text = FONT_SECONDARY_MEDIUM.render(
            'Priority Process Probability', True, Color.WHITE)
        self._io_probability_label_text = FONT_SECONDARY_MEDIUM.render(
            'I/O Probability', True, Color.WHITE)
        self._graceful_termination_label_text = FONT_SECONDARY_MEDIUM.render(
            'Enable Graceful Termination', True, Color.WHITE)

    @property
    def width(self):
        return 560

    @property
    def height(self):
        return 680

    @property
    def label_height(self):
        return self._num_cpus_label_text.get_height()

    @property
    def num_cpus_y(self):
        return self.y + self._title_text.get_height() + 60

    @property
    def num_processes_at_startup_y(self):
        return self.num_cpus_y + self.label_height + 30

    @property
    def max_processes_y(self):
        return self.num_processes_at_startup_y + self.label_height + 30

    @property
    def num_ram_rows_y(self):
        return self.max_processes_y + self.label_height + 30

    @property
    def swap_delay_y(self):
        return self.num_ram_rows_y + self.label_height + 30

    @property
    def new_process_probability_y(self):
        return self.swap_delay_y + self.label_height + 30

    @property
    def priority_process_probability_y(self):
        return self.new_process_probability_y + self.label_height + 30

    @property
    def io_probability_y(self):
        return self.priority_process_probability_y + self.label_height + 30

    @property
    def graceful_termination_y(self):
        return self.io_probability_y + self.label_height + 30

    def draw(self, surface):
        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(
            self.x, self.y, self.width, self.height), border_radius=3)
        pygame.draw.rect(
            surface,
            (70,
             70,
             70),
            pygame.Rect(
                self.x + 2,
                self.y + 2,
                self.width - 4,
                self.height - 4),
            border_radius=3)

        surface.blit(self._title_text, (self.x + (self.width -
                     self._title_text.get_width()) / 2, self.y + 20))
        surface.blit(self._num_cpus_label_text, (self.x + 20, self.num_cpus_y))
        surface.blit(self._num_processes_at_startup_label_text,
                     (self.x + 20, self.num_processes_at_startup_y))
        surface.blit(self._max_processes_label_text,
                     (self.x + 20, self.max_processes_y))
        surface.blit(self._num_ram_rows_label_text,
                     (self.x + 20, self.num_ram_rows_y))
        surface.blit(self._swap_delay_label_text,
                     (self.x + 20, self.swap_delay_y))
        surface.blit(self._new_process_probability_label_text,
                     (self.x + 20, self.new_process_probability_y))
        surface.blit(self._priority_process_probability_label_text,
                     (self.x + 20, self.priority_process_probability_y))
        surface.blit(self._io_probability_label_text,
                     (self.x + 20, self.io_probability_y))
        surface.blit(self._graceful_termination_label_text,
                    (self.x + 20, self.graceful_termination_y))
