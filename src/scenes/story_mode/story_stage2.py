from config.stage_config import StageConfig
from config.cpu_config import CpuConfig
from constants import ONE_MINUTE, SWAP_DELAY_NAMES_TO_MS
from scenes.story_mode.story_stage import StoryStage
from scene_objects.process import ProcessType
from scene_objects.stage_intro_dialog import (
    KilledProcessBadge, Section, TimerBadge,
)

_STAGE_CONFIG = StageConfig(
    cpu_config=CpuConfig(num_cores=1, num_threads_per_core=2),
    num_processes_at_startup=5,
    force_new_priority_process_at_times_ms=[300],
    min_processes_at_times_ms=[
        (250, 5),
        (ONE_MINUTE, 8),
        (2 * ONE_MINUTE, 10),
        (4 * ONE_MINUTE, 12),
        (5 * ONE_MINUTE, 14)
    ],
    max_processes=14,
    max_processes_terminated_by_user=5,
    num_ram_rows=4,
    max_pages_per_process=6,
    swap_delay_ms=SWAP_DELAY_NAMES_TO_MS['High'],
    parallel_swaps=2,
    new_process_probability=0.01,
    priority_process_probability=0,
    io_probability=0.1,
    priority_process_io_probability=0.25,
    io_min_waiting_time_ms=4000,
    io_max_waiting_time_ms=8000,
    graceful_termination_probability=0.01,
    priority_process_graceful_termination_probability=0,
    time_ms_to_show_sort_button=float('inf'),
    time_ms_to_show_auto_sort_checkbox=float('inf'),
)

_INTRO_SECTIONS = [
    Section('Desktop PC', (
        'Single-Core CPU with 2 Threads',
        '512 MB DDR SDRAM',
        '7200 RPM IDE HDD',
        'Ethernet 10/100 Mbps',
    )),
    Section('Victory Conditions', (
        f'Survive 6 minutes with less than '
        f'{_STAGE_CONFIG.max_processes_terminated_by_user} user ragequits',
        'Do not let the user kill the priority process',
    )),
]

_INTRO_BADGES = (
    TimerBadge(6),
    KilledProcessBadge(f'<{_STAGE_CONFIG.max_processes_terminated_by_user}'),
    KilledProcessBadge('0', is_priority=True),
)


class StoryStage2(StoryStage):
    stage_name = 'Stage 2: 2003'
    victory_time_ms = 6 * ONE_MINUTE
    intro_sections = _INTRO_SECTIONS
    intro_badges = _INTRO_BADGES

    def __init__(self):
        super().__init__(_STAGE_CONFIG)

    def check_defeat(self) -> bool | tuple[bool, str]:
        if any(p.type == ProcessType.PRIORITY
               for p in self.process_manager.user_terminated_processes):
            return (True, 'The user killed the priority process.')
        return super().check_defeat()
