import pytest

from constants import ONE_MINUTE, ONE_SECOND
from config.cpu_config import CpuConfig
from config.stage_config import StageConfig
from engine.game_manager import GameManager
from engine.random import Random
from scene_objects.stage_intro_dialog import (
    KilledProcessBadge, Section, StageIntroDialog, TimerBadge,
)
from scenes.story_mode.story_stage import StoryStage


_STAGE_CONFIG = StageConfig(
    cpu_config=CpuConfig(num_cores=1),
    num_processes_at_startup=4,
    max_processes_terminated_by_user=4,
)

_INTRO_SECTIONS = (Section('Desktop PC', ('Single-Core CPU',)),)
_INTRO_BADGES = (
    TimerBadge(3),
    KilledProcessBadge('<4'),
    KilledProcessBadge('0', is_priority=True),
)


class SampleStoryStage(StoryStage):

    stage_name = 'Test Story Stage'
    victory_time_ms = 3 * ONE_MINUTE
    intro_sections = _INTRO_SECTIONS
    intro_badges = _INTRO_BADGES

    def __init__(self):
        super().__init__(_STAGE_CONFIG)


def _advance_uptime_to(stage, uptime_ms):
    stage.uptime_manager.update(0, [])
    for time in range(ONE_SECOND, uptime_ms + 1, ONE_SECOND):
        stage.uptime_manager.update(time, [])


class TestStoryStage:
    @pytest.fixture
    def stage(self, scene_manager):
        stage = SampleStoryStage()
        stage.scene_manager = scene_manager
        stage.setup()
        return stage

    @pytest.fixture
    def ready_stage(self, scene_manager, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)
        stage = SampleStoryStage()
        stage.scene_manager = scene_manager
        stage.setup()
        process_manager = stage.process_manager

        time = 0.0
        process_count = 0
        process_in_motion = 0
        iteration_count = 0

        while (
            (process_count < 4 or process_in_motion > 0)
            and iteration_count < 100000
        ):
            iteration_count += 1
            process_manager.update(int(time), [])
            time += ONE_SECOND / GameManager.fps

            used_process_slots = [
                slot for slot in process_manager.process_slots
                if slot.process is not None
            ]
            process_count = len(used_process_slots)
            process_in_motion = len([
                slot for slot in used_process_slots if slot.process.is_in_motion
            ])

        return stage

    def test_check_victory_returns_false_before_victory_time(self, stage):
        _advance_uptime_to(stage, 3 * ONE_MINUTE - 1)
        assert not stage.check_victory()

    def test_check_victory_returns_true_at_victory_time(self, stage):
        _advance_uptime_to(stage, 3 * ONE_MINUTE)
        assert stage.check_victory()

    def test_check_victory_returns_true_after_victory_time(self, stage):
        _advance_uptime_to(stage, 3 * ONE_MINUTE + 1)
        assert stage.check_victory()

    def test_check_defeat_returns_reason_when_ragequit_limit_reached(self, ready_stage):
        process_manager = ready_stage.process_manager
        for _ in range(4):
            process = next(
                slot.process for slot in process_manager.process_slots
                if slot.process is not None
            )
            process_manager.terminate_process(process, True)

        assert ready_stage.check_defeat() == (True, 'Too many user ragequits.')

    def test_on_start_shows_intro_dialog_with_declared_sections_and_badges(self, stage):
        stage.on_start()

        assert isinstance(stage.modal, StageIntroDialog)
        assert stage.modal.title == 'Test Story Stage'
        assert stage.modal.sections == _INTRO_SECTIONS
        assert stage.modal.badges == _INTRO_BADGES

    def test_on_start_builds_a_new_intro_dialog_each_time(self, stage):
        stage.on_start()
        first_modal = stage.modal

        stage.close_modal()
        stage.on_start()

        assert stage.modal is not first_modal
