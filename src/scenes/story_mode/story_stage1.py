from config.stage_config import StageConfig
from config.cpu_config import CpuConfig
from constants import ONE_MINUTE, SWAP_DELAY_NAMES_TO_MS
from scenes.story_mode.story_stage import StoryStage, SurvivalVictoryCondition
from scene_objects.stage_intro_dialog import Section

_STAGE_CONFIG = StageConfig(
    cpu_config=CpuConfig(num_cores=1),
    num_processes_at_startup=3,
    force_new_high_priority_process_at_times_ms=[100],
    min_processes_at_times_ms=[
        (100, 3),
        (ONE_MINUTE, 4),
        (2 * ONE_MINUTE, 5),
        (4 * ONE_MINUTE, 6),
        (5 * ONE_MINUTE, 8)
    ],
    max_processes=8,
    max_processes_terminated_by_user=5,
    num_ram_rows=1,
    max_pages_per_process=3,
    swap_delay_ms=SWAP_DELAY_NAMES_TO_MS['Higher'],
    parallel_swaps=1,
    new_process_probability=0.01,
    high_priority_process_probability=0,
    io_probability=0.1,
    high_priority_process_io_probability=0.25,
    io_min_waiting_time_ms=5000,
    io_max_waiting_time_ms=10000,
    graceful_termination_probability=0.01,
    high_priority_process_graceful_termination_probability=0,
    time_ms_to_show_sort_button=float('inf'),
    time_ms_to_show_auto_sort_checkbox=float('inf'),
)

_VICTORY_CONDITIONS = (
    SurvivalVictoryCondition(
        minutes=6,
        max_terminated_process=_STAGE_CONFIG.max_processes_terminated_by_user,
        max_terminated_high_priority_process=0),
)

_INTRO_SECTIONS = [
    Section('Desktop PC', (
        'Single-Core CPU',
        '32 MB SDRAM',
        '5400 RPM IDE HDD',
        'Dial-Up Modem',
    )),
]


class StoryStage1(StoryStage):
    stage_name = 'Stage 1: 1998'
    victory_conditions = _VICTORY_CONDITIONS
    intro_sections = _INTRO_SECTIONS

    def __init__(self):
        super().__init__(_STAGE_CONFIG)
