from scenes.stage import Stage
from config.stage_config import StageConfig
from config.cpu_config import CpuConfig
from constants import SWAP_DELAY_NAMES_TO_MS
from scene_objects.stage_intro_dialog import Section, StageIntroDialog

_stage_config = StageConfig(
    cpu_config=CpuConfig(num_cores=1),
    num_processes_at_startup=3,
    force_new_priority_process_at_times_ms=[100],
    max_processes=10,
    max_processes_terminated_by_user=5,
    num_ram_rows=1,
    swap_delay_ms=SWAP_DELAY_NAMES_TO_MS['Higher'],
    parallel_swaps=1,
    new_process_probability=0.05,
    priority_process_probability=0,
    io_probability=0.1,
    priority_process_io_probability=0.25,
    io_min_waiting_time_ms=5000,
    io_max_waiting_time_ms=10000,
    graceful_termination_probability=0.01,
    priority_process_graceful_termination_probability=0,
    time_ms_to_show_sort_button=float('inf'),
    time_ms_to_show_auto_sort_checkbox=float('inf'),
)

_INTRO_SECTIONS = [
    Section('Desktop PC', (
        'Single-Core CPU',
        '32 MB SDRAM',
        '4200 RPM IDE HDD',
        'Dial-Up Modem',
    )),
    Section('Victory Conditions', (
        'Survive 5 minutes with less than 5 user ragequits',
        'Do not let the user kill any priority process',
    )),
]


class StoryStage1(Stage):
    def __init__(self):
        super().__init__('Stage 1: 1998', _stage_config)

    def on_start(self):
        self.show_modal(StageIntroDialog('Stage 1: 1998', _INTRO_SECTIONS))
