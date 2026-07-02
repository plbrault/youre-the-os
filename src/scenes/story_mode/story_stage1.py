from scenes.stage import Stage
from config.stage_config import StageConfig
from config.cpu_config import CpuConfig
from constants import ONE_MINUTE, SWAP_DELAY_NAMES_TO_MS
from scene_objects.process import ProcessType
from scene_objects.stage_intro_dialog import Badge, Section, StageIntroDialog
from scene_objects.story_stage_result_dialog import StoryStageResultDialog

_stage_config = StageConfig(
    cpu_config=CpuConfig(num_cores=1),
    num_processes_at_startup=3,
    force_new_priority_process_at_times_ms=[100, 5.25 * ONE_MINUTE],
    min_processes_at_times_ms=[
        (100, 3),
        (ONE_MINUTE, 4),
        (2 * ONE_MINUTE, 5),
        (3 * ONE_MINUTE, 6),
        (4.5 * ONE_MINUTE, 7),
        (5 * ONE_MINUTE, 8),
    ],
    max_processes=9,
    max_processes_terminated_by_user=4,
    num_ram_rows=1,
    max_pages_per_process=3,
    swap_delay_ms=SWAP_DELAY_NAMES_TO_MS['Higher'],
    parallel_swaps=1,
    new_process_probability=0,
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
        '5400 RPM IDE HDD',
        'Dial-Up Modem',
    )),
    Section('Victory Conditions', (
        f'Survive 6 minutes with less than '
        f'{_stage_config.max_processes_terminated_by_user} user ragequits',
        'Do not let the user kill any priority process',
    )),
]


class StoryStage1(Stage):
    def __init__(self):
        super().__init__('Stage 1: 1998', _stage_config)

    def on_start(self):
        self.show_modal(StageIntroDialog(
            'Stage 1: 1998',
            _INTRO_SECTIONS,
            badges=(
                Badge(_stage_config.max_processes_terminated_by_user),
                Badge(0, is_priority=True),
            ),
        ))

    def check_victory(self) -> bool:
        return self.uptime_manager.uptime_ms >= 6 * ONE_MINUTE

    def check_defeat(self) -> bool | tuple[bool, str]:
        if any(p.type == ProcessType.PRIORITY
               for p in self.process_manager.user_terminated_processes):
            return (True, 'The user killed a priority process.')
        if super().check_defeat():
            return (True, 'Too many user ragequits.')
        return False

    def on_victory(self):
        self.show_modal(StoryStageResultDialog(
            is_victory=True,
            uptime=self._uptime_manager.uptime_text,
            stage_name=self.name,
            score=self._score_manager.score,
            restart_game_fn=self.reset,
            main_menu_fn=self._return_to_main_menu,
            standalone=self._standalone,
        ))

    def on_defeat(self, reason: str | None = None):
        self.show_modal(StoryStageResultDialog(
            is_victory=False,
            uptime=self._uptime_manager.uptime_text,
            stage_name=self.name,
            score=self._score_manager.score,
            reason=reason,
            restart_game_fn=self.reset,
            main_menu_fn=self._return_to_main_menu,
            standalone=self._standalone,
        ))
