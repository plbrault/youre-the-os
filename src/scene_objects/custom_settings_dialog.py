from dataclasses import replace

from constants import (
    MIN_CPU_COUNT, MAX_CPU_COUNT, MIN_PROCESSES_AT_STARTUP,
    MAX_PROCESSES_AT_STARTUP, MAX_PROCESSES, MIN_RAM_ROWS, MAX_RAM_ROWS,
    SWAP_DELAY_NAMES, SWAP_DELAY_NAMES_TO_MS, PAGES_PER_ROW
)
from engine.modal import Modal
from scene_objects.button import Button
from scene_objects.option_selector import OptionSelector
from scene_objects.views.custom_settings_dialog_view import CustomSettingsDialogView
from config.cpu_config import CpuConfig
from config.stage_config import StageConfig

_swap_delay_ms_to_ids = {
    SWAP_DELAY_NAMES_TO_MS[name]: idx for idx, name in enumerate(SWAP_DELAY_NAMES)
}

class CustomSettingsDialog(Modal):

    def __init__(self, start_fn, default_config : StageConfig = StageConfig()):
        super().__init__(CustomSettingsDialogView(self))

        self.num_cpus_selector = OptionSelector(
            [str(i) for i in range(MIN_CPU_COUNT, MAX_CPU_COUNT + 1)],
            default_config.cpu_config.num_cores - 1
        )
        self.children.append(self.num_cpus_selector)

        self.num_processes_at_startup_selector = OptionSelector(
            [str(i) for i in range(MIN_PROCESSES_AT_STARTUP, MAX_PROCESSES_AT_STARTUP + 1)],
            default_config.num_processes_at_startup - 1
        )
        self.children.append(self.num_processes_at_startup_selector)

        self.max_processes_selector = OptionSelector(
            [str(i) for i in range(MIN_PROCESSES_AT_STARTUP, MAX_PROCESSES + 1)],
            default_config.max_processes - 1
        )
        self.children.append(self.max_processes_selector)

        self.num_ram_rows_selector = OptionSelector(
            [str(i) for i in range(MIN_RAM_ROWS, MAX_RAM_ROWS + 1)],
            default_config.num_ram_rows - 1)
        self.children.append(self.num_ram_rows_selector)

        self.swap_delay_selector = OptionSelector(
            SWAP_DELAY_NAMES,
            _swap_delay_ms_to_ids[default_config.swap_delay_ms]
        )
        self.children.append(self.swap_delay_selector)

        self.parallel_swap_selector = OptionSelector(
            [str(i) for i in range(1, PAGES_PER_ROW + 1)],
            default_config.parallel_swaps - 1
        )
        self.children.append(self.parallel_swap_selector)

        self.new_process_probability_selector = OptionSelector(
            [str(i) + ' %' for i in range(0, 105, 5)])
        self.new_process_probability_selector.selected_option = str(
            int(default_config.new_process_probability * 100)) + ' %'
        self.children.append(self.new_process_probability_selector)

        self.priority_process_probability_selector = OptionSelector(
            ['0 %', '1 %', '2 %']
            +
            [str(i) + ' %' for i in range(5, 105, 5)]
        )
        self.priority_process_probability_selector.selected_option = str(
            int(default_config.priority_process_probability * 100)) + ' %'
        self.children.append(self.priority_process_probability_selector)

        self.io_probability_selector = OptionSelector(
            ['0 %', '1 %']
            +
            [str(i) + ' %' for i in range(5, 55, 5)]
        )
        self.io_probability_selector.selected_option = str(
            int(default_config.io_probability * 100)) + ' %'
        self.children.append(self.io_probability_selector)

        self.graceful_termination_selector = OptionSelector(['Yes', 'No'])
        self.graceful_termination_selector.selected_option = (
            'Yes'
            if default_config.graceful_termination_probability > 0
            else 'No'
        )
        self.children.append(self.graceful_termination_selector)

        selector_width = self.swap_delay_selector.view.width
        self.num_cpus_selector.view.min_width = selector_width
        self.num_processes_at_startup_selector.view.min_width = selector_width
        self.max_processes_selector.view.min_width = selector_width
        self.new_process_probability_selector.view.min_width = selector_width
        self.num_ram_rows_selector.view.min_width = selector_width
        self.swap_delay_selector.view.min_width = selector_width
        self.parallel_swap_selector.view.min_width = selector_width
        self.io_probability_selector.view.min_width = selector_width
        self.priority_process_probability_selector.view.min_width = selector_width
        self.graceful_termination_selector.view.min_width = selector_width

        self.start_button = Button('Start', start_fn)
        self.children.append(self.start_button)

        self.cancel_button = Button('Cancel', self.close)
        self.children.append(self.cancel_button)

    @property
    def config(self):
        config = StageConfig(
            cpu_config = CpuConfig(num_cores = int(self.num_cpus_selector.selected_option)),
            num_processes_at_startup = int(self.num_processes_at_startup_selector.selected_option),
            max_processes = int(self.max_processes_selector.selected_option),
            num_ram_rows = int(self.num_ram_rows_selector.selected_option),
            swap_delay_ms = SWAP_DELAY_NAMES_TO_MS[self.swap_delay_selector.selected_option],
            parallel_swaps = int(self.parallel_swap_selector.selected_option),
            new_process_probability = (
                self.new_process_probability_selector.selected_option_id * 0.05
            ),
            priority_process_probability = (
                [0, 0.01, 0.02]
                + [i / 100 for i in range(5, 105, 5)]
            )[self.priority_process_probability_selector.selected_option_id],
            io_probability = (
                [0, 0.01]
                + [i / 100 for i in range(5, 105, 5)]
            )[self.io_probability_selector.selected_option_id],
        )

        if self.graceful_termination_selector.selected_option == 'No':
            config = replace(config, graceful_termination_probability = 0)

        return config

    def update(self, current_time, events):
        self.num_processes_at_startup_selector.in_error = (
            self.num_processes_at_startup_selector.selected_option_id
            > self.max_processes_selector.selected_option_id
        )
        self.max_processes_selector.in_error = self.num_processes_at_startup_selector.in_error
        self.start_button.disabled = self.max_processes_selector.in_error

        for child in self.children:
            child.update(current_time, events)
