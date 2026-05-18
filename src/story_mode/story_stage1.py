from scenes.stage import Stage
from config.stage_config import StageConfig
from config.cpu_config import CpuConfig
from constants import SWAP_DELAY_NAMES_TO_MS

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
    time_ms_to_show_sort_button = float('inf'),
    time_ms_to_show_auto_sort_checkbox = float('inf'),
)

class StoryStage1(Stage):
    def __init__(self):
        super().__init__('Stage 1: 1998', _stage_config)
