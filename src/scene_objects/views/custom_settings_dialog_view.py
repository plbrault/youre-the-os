from engine.modal_view import ModalView
from ui.fonts import FONT_SECONDARY_MEDIUM, FONT_PRIMARY_XXLARGE
from ui.color import Color

_OPTION_VERTICAL_SPACING = 25

class CustomSettingsDialogView(ModalView):
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
        self._parallel_swap_label_text = FONT_SECONDARY_MEDIUM.render(
            'Parallel Swaps', True, Color.WHITE)
        self._new_process_probability_label_text = FONT_SECONDARY_MEDIUM.render(
            'New Process Probability', True, Color.WHITE)
        self._priority_process_probability_label_text = FONT_SECONDARY_MEDIUM.render(
            'Priority Process Probability', True, Color.WHITE)
        self._io_probability_label_text = FONT_SECONDARY_MEDIUM.render(
            'I/O Probability', True, Color.WHITE)
        self._graceful_termination_label_text = FONT_SECONDARY_MEDIUM.render(
            'Enable Graceful Termination', True, Color.WHITE)

    @ModalView.x.setter
    def x(self, value):
        self._x = value
        dialog = self._custom_settings_dialog
        right_edge = self.x + self.width - 20
        dialog.num_cpus_selector.view.x = right_edge - dialog.num_cpus_selector.view.width
        dialog.num_processes_at_startup_selector.view.x = (
            right_edge - dialog.num_processes_at_startup_selector.view.width)
        dialog.max_processes_selector.view.x = (
            right_edge - dialog.max_processes_selector.view.width)
        dialog.num_ram_rows_selector.view.x = (
            right_edge - dialog.num_ram_rows_selector.view.width)
        dialog.swap_delay_selector.view.x = (
            right_edge - dialog.swap_delay_selector.view.width)
        dialog.parallel_swap_selector.view.x = (
            right_edge - dialog.parallel_swap_selector.view.width)
        dialog.new_process_probability_selector.view.x = (
            right_edge - dialog.new_process_probability_selector.view.width)
        dialog.priority_process_probability_selector.view.x = (
            right_edge - dialog.priority_process_probability_selector.view.width)
        dialog.io_probability_selector.view.x = (
            right_edge - dialog.io_probability_selector.view.width)
        dialog.graceful_termination_selector.view.x = (
            right_edge - dialog.graceful_termination_selector.view.width)
        dialog.start_button.view.x = (
            self.x + (self.width / 2) - dialog.start_button.view.width - 10)
        dialog.cancel_button.view.x = self.x + (self.width / 2) + 10

    @ModalView.y.setter
    def y(self, value):
        self._y = value
        dialog = self._custom_settings_dialog
        label_h = self.label_height
        dialog.num_cpus_selector.view.y = (
            self.num_cpus_y + (label_h - dialog.num_cpus_selector.view.height) / 2)
        dialog.num_processes_at_startup_selector.view.y = (
            self.num_processes_at_startup_y
            + (label_h - dialog.num_processes_at_startup_selector.view.height) / 2)
        dialog.max_processes_selector.view.y = (
            self.max_processes_y + (label_h - dialog.max_processes_selector.view.height) / 2)
        dialog.num_ram_rows_selector.view.y = (
            self.num_ram_rows_y + (label_h - dialog.num_ram_rows_selector.view.height) / 2)
        dialog.swap_delay_selector.view.y = (
            self.swap_delay_y + (label_h - dialog.swap_delay_selector.view.height) / 2)
        dialog.parallel_swap_selector.view.y = (
            self.parallel_swap_y + (label_h - dialog.parallel_swap_selector.view.height) / 2)
        dialog.new_process_probability_selector.view.y = (
            self.new_process_probability_y
            + (label_h - dialog.new_process_probability_selector.view.height) / 2)
        dialog.priority_process_probability_selector.view.y = (
            self.priority_process_probability_y
            + (label_h - dialog.priority_process_probability_selector.view.height) / 2)
        dialog.io_probability_selector.view.y = (
            self.io_probability_y + (label_h - dialog.io_probability_selector.view.height) / 2)
        dialog.graceful_termination_selector.view.y = (
            self.graceful_termination_y
            + (label_h - dialog.graceful_termination_selector.view.height) / 2)
        dialog.start_button.view.y = self.y + self.height - dialog.start_button.view.height - 18
        dialog.cancel_button.view.y = self.y + self.height - dialog.cancel_button.view.height - 18

    @property
    def width(self):
        return 580

    @property
    def height(self):
        return 680

    @property
    def label_height(self):
        return self._num_cpus_label_text.get_height()

    @property
    def num_cpus_y(self):
        return self.y + self._title_text.get_height() + 50

    @property
    def num_processes_at_startup_y(self):
        return self.num_cpus_y + self.label_height + _OPTION_VERTICAL_SPACING

    @property
    def max_processes_y(self):
        return self.num_processes_at_startup_y + self.label_height + _OPTION_VERTICAL_SPACING

    @property
    def num_ram_rows_y(self):
        return self.max_processes_y + self.label_height + _OPTION_VERTICAL_SPACING

    @property
    def swap_delay_y(self):
        return self.num_ram_rows_y + self.label_height + _OPTION_VERTICAL_SPACING

    @property
    def parallel_swap_y(self):
        return self.swap_delay_y + self.label_height + _OPTION_VERTICAL_SPACING

    @property
    def new_process_probability_y(self):
        return self.parallel_swap_y + self.label_height + _OPTION_VERTICAL_SPACING

    @property
    def priority_process_probability_y(self):
        return self.new_process_probability_y + self.label_height + _OPTION_VERTICAL_SPACING

    @property
    def io_probability_y(self):
        return self.priority_process_probability_y + self.label_height + _OPTION_VERTICAL_SPACING

    @property
    def graceful_termination_y(self):
        return self.io_probability_y + self.label_height + _OPTION_VERTICAL_SPACING

    def draw_content(self, surface):
        surface.blit(self._title_text, (self.x + (self.width -
                     self._title_text.get_width()) / 2, self.y + 18))
        surface.blit(self._num_cpus_label_text, (self.x + 20, self.num_cpus_y))
        surface.blit(self._num_processes_at_startup_label_text,
                     (self.x + 20, self.num_processes_at_startup_y))
        surface.blit(self._max_processes_label_text,
                     (self.x + 20, self.max_processes_y))
        surface.blit(self._num_ram_rows_label_text,
                     (self.x + 20, self.num_ram_rows_y))
        surface.blit(self._swap_delay_label_text,
                     (self.x + 20, self.swap_delay_y))
        surface.blit(self._parallel_swap_label_text,
                     (self.x + 20, self.parallel_swap_y))
        surface.blit(self._new_process_probability_label_text,
                     (self.x + 20, self.new_process_probability_y))
        surface.blit(self._priority_process_probability_label_text,
                     (self.x + 20, self.priority_process_probability_y))
        surface.blit(self._io_probability_label_text,
                     (self.x + 20, self.io_probability_y))
        surface.blit(self._graceful_termination_label_text,
                    (self.x + 20, self.graceful_termination_y))
