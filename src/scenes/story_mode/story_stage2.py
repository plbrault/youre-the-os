from config.stage_config import StageConfig
from config.cpu_config import CpuConfig
from constants import ONE_MINUTE, SWAP_DELAY_NAMES_TO_MS
from scenes.story_mode.story_stage import StoryStage, SurvivalVictoryCondition
from scene_objects.stage_intro_dialog import Section

_STAGE_CONFIG = StageConfig(
    cpu_config=CpuConfig(num_cores=1, num_threads_per_core=2, penalty_ms=1000),
    num_processes_at_startup=5,
    force_new_high_priority_process_at_times_ms=[300],
    min_processes_at_times_ms=[
        (250, 5),
        (ONE_MINUTE, 6),
        (2 * ONE_MINUTE, 8),
        (4 * ONE_MINUTE, 10),
        (5 * ONE_MINUTE, 12),
        (6 * ONE_MINUTE, 14)
    ],
    max_processes=14,
    max_processes_terminated_by_user=5,
    num_ram_rows=3,
    max_pages_per_process=5,
    swap_delay_ms=SWAP_DELAY_NAMES_TO_MS['High'],
    parallel_swaps=2,
    new_process_probability=0.01,
    high_priority_process_probability=0,
    io_probability=0.1,
    high_priority_process_io_probability=0.25,
    io_min_waiting_time_ms=4000,
    io_max_waiting_time_ms=8000,
    graceful_termination_probability=0.01,
    high_priority_process_graceful_termination_probability=0,
    time_ms_to_show_sort_button=float('inf'),
    time_ms_to_show_auto_sort_checkbox=float('inf'),
)

_VICTORY_CONDITIONS = (
    SurvivalVictoryCondition(
        minutes=7,
        max_terminated_process=_STAGE_CONFIG.max_processes_terminated_by_user,
        max_terminated_high_priority_process=0),
)

_INTRO_SECTIONS = [
    Section('Desktop PC', (
        'Single-Core CPU with 2 Threads',
        '512 MB DDR SDRAM',
        '7200 RPM IDE HDD',
        'Ethernet 10/100 Mbps',
    )),
]


class StoryStage2(StoryStage):
    stage_name = 'Stage 2: 2003'
    victory_conditions = _VICTORY_CONDITIONS
    intro_sections = _INTRO_SECTIONS

    def __init__(self):
        super().__init__(_STAGE_CONFIG)
