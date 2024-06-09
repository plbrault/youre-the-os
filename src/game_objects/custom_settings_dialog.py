from dataclasses import replace

from constants import (
    MIN_CPU_COUNT, MAX_CPU_COUNT, MIN_PROCESSES_AT_STARTUP,
    MAX_PROCESSES_AT_STARTUP, MAX_PROCESSES, MIN_RAM_ROWS, MAX_RAM_ROWS
)
from engine.game_object import GameObject
from game_objects.button import Button
from game_objects.option_selector import OptionSelector
from game_objects.views.custom_settings_dialog_view import CustomSettingsDialogView
from stage_config import StageConfig

class CustomSettingsDialog(GameObject):

    def __init__(self, start_fn, cancel_fn, default_config : StageConfig = StageConfig()):
        super().__init__(CustomSettingsDialogView(self))

        self._num_cpus_selector = OptionSelector(
            [str(i) for i in range(MIN_CPU_COUNT, MAX_CPU_COUNT + 1)], default_config.num_cpus - 1)
        self.children.append(self._num_cpus_selector)

        self._num_processes_at_startup_selector = OptionSelector(
            [str(i) for i in range(MIN_PROCESSES_AT_STARTUP, MAX_PROCESSES_AT_STARTUP + 1)],
            default_config.num_processes_at_startup - 1
        )
        self.children.append(self._num_processes_at_startup_selector)

        self._max_processes_selector = OptionSelector(
            [str(i) for i in range(MIN_PROCESSES_AT_STARTUP, MAX_PROCESSES + 1)],
            default_config.max_processes - 1
        )
        self.children.append(self._max_processes_selector)

        self._num_ram_rows_selector = OptionSelector(
            [str(i) for i in range(MIN_RAM_ROWS, MAX_RAM_ROWS + 1)],
            default_config.num_ram_rows - 1)
        self.children.append(self._num_ram_rows_selector)

        self._new_process_probability_selector = OptionSelector(
            [str(i) + ' %' for i in range(0, 105, 5)])
        self._new_process_probability_selector.selected_option = str(
            int(default_config.new_process_probability * 100)) + ' %'
        self.children.append(self._new_process_probability_selector)

        self._priority_process_probability_selector = OptionSelector(
            ['0 %', '1 %', '2 %']
            +
            [str(i) + ' %' for i in range(5, 105, 5)]
        )
        self._priority_process_probability_selector.selected_option = str(
            int(default_config.priority_process_probability * 100)) + ' %'
        self.children.append(self._priority_process_probability_selector)

        self._io_probability_selector = OptionSelector(
            ['0 %', '1 %']
            +
            [str(i) + ' %' for i in range(5, 55, 5)]
        )
        self._io_probability_selector.selected_option = str(
            int(default_config.io_probability * 100)) + ' %'
        self.children.append(self._io_probability_selector)

        self._graceful_termination_selector = OptionSelector(['Yes', 'No'])
        self._graceful_termination_selector.selected_option = (
            'Yes'
            if default_config.graceful_termination_probability > 0
            else 'No'
        )
        self.children.append(self._graceful_termination_selector)

        selector_width = self._new_process_probability_selector.view.width
        self._num_cpus_selector.view.min_width = selector_width
        self._num_processes_at_startup_selector.view.min_width = selector_width
        self._max_processes_selector.view.min_width = selector_width
        self._num_ram_rows_selector.view.min_width = selector_width
        self._io_probability_selector.view.min_width = selector_width
        self._graceful_termination_selector.view.min_width = selector_width

        self._start_button = Button('Start', start_fn)
        self.children.append(self._start_button)

        self._cancel_button = Button('Cancel', cancel_fn)
        self.children.append(self._cancel_button)

    @property
    def config(self):
        config = StageConfig(
            num_cpus = int(self._num_cpus_selector.selected_option),
            num_processes_at_startup = int(self._num_processes_at_startup_selector.selected_option),
            max_processes = int(self._max_processes_selector.selected_option),
            num_ram_rows = int(self._num_ram_rows_selector.selected_option),
            new_process_probability = (
                self._new_process_probability_selector.selected_option_id * 0.05
            ),
            priority_process_probability = (
                [0, 0.01, 0.02]
                + [i / 100 for i in range(5, 105, 5)]
            )[self._priority_process_probability_selector.selected_option_id],
            io_probability = (
                [0, 0.01]
                + [i / 100 for i in range(5, 105, 5)]
            )[self._io_probability_selector.selected_option_id],
        )

        if self._graceful_termination_selector.selected_option == 'No':
            config = replace(config, graceful_termination_probability = 0)

        return config

    def update(self, current_time, events):
        self._num_processes_at_startup_selector.in_error = (
            self._num_processes_at_startup_selector.selected_option_id
            > self._max_processes_selector.selected_option_id
        )
        self._max_processes_selector.in_error = self._num_processes_at_startup_selector.in_error
        self._start_button.disabled = self._max_processes_selector.in_error

        self._num_cpus_selector.view.set_xy(
            self.view.x + self.view.width - self._num_cpus_selector.view.width - 20,
            self.view.num_cpus_y +
            (self.view.label_height - self._num_cpus_selector.view.height) / 2
        )
        self._num_processes_at_startup_selector.view.set_xy(
            self.view.x + self.view.width - self._num_processes_at_startup_selector.view.width - 20,
            self.view.num_processes_at_startup_y +
            (self.view.label_height - self._num_processes_at_startup_selector.view.height) / 2
        )
        self._max_processes_selector.view.set_xy(
            self.view.x + self.view.width - self._max_processes_selector.view.width - 20,
            self.view.max_processes_y +
            (self.view.label_height - self._max_processes_selector.view.height) / 2
        )
        self._num_ram_rows_selector.view.set_xy(
            self.view.x + self.view.width - self._num_ram_rows_selector.view.width - 20,
            self.view.num_ram_rows_y +
            (self.view.label_height - self._num_ram_rows_selector.view.height) / 2
        )
        self._new_process_probability_selector.view.set_xy(
            self.view.x + self.view.width -
            self._new_process_probability_selector.view.width - 20,
            self.view.new_process_probability_y +
            (self.view.label_height -
             self._new_process_probability_selector.view.height) / 2
        )
        self._priority_process_probability_selector.view.set_xy(
            self.view.x + self.view.width -
            self._priority_process_probability_selector.view.width - 20,
            self.view.priority_process_probability_y +
            (self.view.label_height -
             self._priority_process_probability_selector.view.height) / 2
        )
        self._io_probability_selector.view.set_xy(
            self.view.x + self.view.width - self._io_probability_selector.view.width - 20,
            self.view.io_probability_y +
            (self.view.label_height - self._io_probability_selector.view.height) / 2
        )
        self._graceful_termination_selector.view.set_xy(
            self.view.x + self.view.width - self._graceful_termination_selector.view.width - 20,
            self.view.graceful_termination_y +
            (self.view.label_height - self._graceful_termination_selector.view.height) / 2
        )
        self._start_button.view.set_xy(
            self.view.x + (self.view.width / 2) -
            self._start_button.view.width - 10,
            self.view.y + self.view.height - self._start_button.view.height - 20
        )
        self._cancel_button.view.set_xy(
            self.view.x + (self.view.width / 2) + 10,
            self.view.y + self.view.height - self._cancel_button.view.height - 20
        )

        for child in self.children:
            child.update(current_time, events)
