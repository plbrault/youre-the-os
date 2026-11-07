import pytest

from constants import ONE_MINUTE, ONE_SECOND
from config.cpu_config import CpuConfig
from config.stage_config import StageConfig
from scene_objects.stage_intro_dialog import (
    KilledProcessBadge, Section, StageIntroDialog, TimerBadge,
)
from scenes.story_mode.story_stage import StoryStage


_STAGE_CONFIG = StageConfig(
    cpu_config=CpuConfig(num_cores=1),
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

    def test_check_victory_returns_false_before_victory_time(self, stage):
        _advance_uptime_to(stage, 3 * ONE_MINUTE - 1)
        assert not stage.check_victory()

    def test_check_victory_returns_true_at_victory_time(self, stage):
        _advance_uptime_to(stage, 3 * ONE_MINUTE)
        assert stage.check_victory()

    def test_check_victory_returns_true_after_victory_time(self, stage):
        _advance_uptime_to(stage, 3 * ONE_MINUTE + 1)
        assert stage.check_victory()

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
