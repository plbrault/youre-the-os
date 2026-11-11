import pytest

from constants import ONE_MINUTE, ONE_SECOND
from engine.game_manager import GameManager
from engine.random import Random
from scene_objects.process import ProcessType
from scene_objects.stage_intro_dialog import StageIntroDialog, TimerBadge
from scene_objects.story_stage_defeat_dialog import StoryStageDefeatDialog
from scene_objects.story_stage_victory_dialog import StoryStageVictoryDialog
from scenes.story_mode.story_stage2 import StoryStage2


def _advance_uptime_to(stage, uptime_ms):
    stage.uptime_manager.update(0, [])
    for time in range(ONE_SECOND, uptime_ms + 1, ONE_SECOND):
        stage.uptime_manager.update(time, [])


class TestStoryStage2:
    @pytest.fixture
    def stage(self, scene_manager):
        stage = StoryStage2()
        stage.scene_manager = scene_manager
        stage.setup()
        return stage

    @pytest.fixture
    def ready_stage(self, scene_manager, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)
        stage = StoryStage2()
        stage.scene_manager = scene_manager
        stage.setup()
        process_manager = stage.process_manager

        time = 0.0
        process_count = 0
        process_in_motion = 0
        iteration_count = 0

        while (
            (process_count < 5 or process_in_motion > 0)
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

    def test_check_victory_returns_false_before_seven_minutes(self, stage):
        _advance_uptime_to(stage, 7 * ONE_MINUTE - 1)
        assert not stage.check_victory()

    def test_check_victory_returns_true_at_seven_minutes(self, stage):
        _advance_uptime_to(stage, 7 * ONE_MINUTE)
        assert stage.check_victory()

    def test_check_victory_returns_true_after_seven_minutes(self, stage):
        _advance_uptime_to(stage, 7 * ONE_MINUTE + 1)
        assert stage.check_victory()

    def test_check_defeat_returns_false_when_no_process_terminated(self, ready_stage):
        assert not ready_stage.check_defeat()

    def test_check_defeat_returns_false_when_only_standard_process_terminated(self, ready_stage):
        process_manager = ready_stage.process_manager
        standard_process = next(
            slot.process for slot in process_manager.process_slots
            if slot.process is not None and slot.process.type == ProcessType.STANDARD
        )
        process_manager.terminate_process(standard_process, True)
        assert not ready_stage.check_defeat()

    def test_check_defeat_returns_true_when_high_priority_process_terminated(self, ready_stage):
        process_manager = ready_stage.process_manager
        high_priority_process = next(
            slot.process for slot in process_manager.process_slots
            if slot.process is not None and slot.process.type == ProcessType.HIGH_PRIORITY
        )
        process_manager.terminate_process(high_priority_process, True)
        assert ready_stage.check_defeat() == (True, 'The user killed a high-priority process.')

    def test_on_victory_shows_victory_dialog(self, stage):
        assert stage.active_modal is None

        stage.on_victory()

        assert isinstance(stage.active_modal, StoryStageVictoryDialog)
        assert stage.active_modal.stage_name == 'Stage 2: 2003'
        assert stage.active_modal.score == 0
        assert stage.active_modal.uptime == '0:00:00'
        assert stage.active_modal.primary_button.text == 'Next Stage'
        assert stage.active_modal.main_menu_button.text == 'Main Menu'

    def test_on_defeat_shows_defeat_dialog_with_reason(self, stage):
        assert stage.active_modal is None

        stage.on_defeat('The user killed a high-priority process.')

        assert isinstance(stage.active_modal, StoryStageDefeatDialog)
        assert stage.active_modal.reason == 'The user killed a high-priority process.'
        assert stage.active_modal.stage_name == 'Stage 2: 2003'
        assert stage.active_modal.score == 0
        assert stage.active_modal.uptime == '0:00:00'
        assert stage.active_modal.primary_button.text == 'Try Again'
        assert stage.active_modal.main_menu_button.text == 'Main Menu'

    def test_on_victory_in_standalone_mode_shows_actual_stage_name(self, stage):
        stage.standalone = True

        stage.on_victory()

        assert stage.active_modal.stage_name == 'Stage 2: 2003'

    def test_on_start_shows_intro_dialog_with_seven_minute_timer_badge(self, stage):
        stage.on_start()

        assert isinstance(stage.active_modal, StageIntroDialog)
        timer_badges = [b for b in stage.active_modal.badges if isinstance(b, TimerBadge)]
        assert timer_badges == [TimerBadge(7)]
