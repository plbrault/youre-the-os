from scenes.stage import Stage
from config.stage_config import StageConfig
from config.cpu_config import CpuConfig
from constants import ONE_MINUTE, SWAP_DELAY_NAMES_TO_MS
from scene_objects.process import ProcessType
from scene_objects.stage_intro_dialog import (
    KilledProcessBadge, Section, StageIntroDialog, TimerBadge,
)
from scene_objects.story_stage_defeat_dialog import StoryStageDefeatDialog
from scene_objects.story_stage_victory_dialog import StoryStageVictoryDialog

_stage_config = StageConfig(
    cpu_config=CpuConfig(num_cores=1, num_threads_per_core=2),
    num_processes_at_startup=5,
    force_new_priority_process_at_times_ms=[100, 4 * ONE_MINUTE],
    min_processes_at_times_ms=[
        (100, 6),
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
        f'{_stage_config.max_processes_terminated_by_user} user ragequits',
        'Do not let the user kill a priority process',
    )),
]


class StoryStage2(Stage):

    def __init__(self):
        super().__init__('Stage 2: 2003', _stage_config)

    def on_start(self):
        self.show_modal(StageIntroDialog(
            self.name,
            _INTRO_SECTIONS,
            badges=(
                TimerBadge(6),
                KilledProcessBadge(
                    f'<{_stage_config.max_processes_terminated_by_user}'),
                KilledProcessBadge('0', is_priority=True),
            ),
        ))

    def check_victory(self) -> bool:
        return self.uptime_manager.uptime_ms >= 6 * ONE_MINUTE

    def check_defeat(self) -> bool | tuple[bool, str]:
        if any(p.type == ProcessType.PRIORITY
               for p in self.process_manager.user_terminated_processes):
            return (True, 'The user killed the priority process.')
        if super().check_defeat():
            return (True, 'Too many user ragequits.')
        return False

    def on_victory(self):
        self.show_modal(StoryStageVictoryDialog(
            uptime=self._uptime_manager.uptime_text,
            stage_name=self.name,
            score=self._score_manager.score,
            next_stage_fn=self._go_to_next_stage,
            main_menu_fn=self._return_to_main_menu,
            standalone=self._standalone,
        ))

    def _go_to_next_stage(self):
        pass

    def on_defeat(self, reason: str | None = None):
        self.show_modal(StoryStageDefeatDialog(
            uptime=self._uptime_manager.uptime_text,
            stage_name=self.name,
            score=self._score_manager.score,
            reason=reason,
            restart_stage_fn=self.reset,
            main_menu_fn=self._return_to_main_menu,
            standalone=self._standalone,
        ))
