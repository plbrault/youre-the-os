import pytest

from constants import ONE_MINUTE, ONE_SECOND
from engine.game_manager import GameManager
from engine.random import Random
from scene_objects.process import ProcessType
from scene_objects.story_stage_result_dialog import StoryStageResultDialog
from scenes.story_mode.story_stage1 import StoryStage1


class TestStoryStage1:
    @pytest.fixture
    def stage(self, scene_manager):
        stage = StoryStage1()
        stage.scene_manager = scene_manager
        stage.setup()
        return stage

    @pytest.fixture
    def ready_stage(self, scene_manager, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)
        stage = StoryStage1()
        stage.scene_manager = scene_manager
        stage.setup()
        process_manager = stage.process_manager

        time = 0.0
        process_count = 0
        process_in_motion = 0
        iteration_count = 0

        while (
            (process_count < 3 or process_in_motion > 0)
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

    def test_check_victory_returns_false_before_five_minutes(self, stage):
        assert not stage.check_victory(5 * ONE_MINUTE - 1)

    def test_check_victory_returns_true_at_five_minutes(self, stage):
        assert stage.check_victory(5 * ONE_MINUTE)

    def test_check_victory_returns_true_after_five_minutes(self, stage):
        assert stage.check_victory(5 * ONE_MINUTE + 1)

    def test_check_defeat_returns_false_when_no_process_terminated(self, ready_stage):
        assert not ready_stage.check_defeat(0)

    def test_check_defeat_returns_false_when_only_standard_process_terminated(self, ready_stage):
        process_manager = ready_stage.process_manager
        standard_process = next(
            slot.process for slot in process_manager.process_slots
            if slot.process is not None and slot.process.type == ProcessType.STANDARD
        )
        process_manager.terminate_process(standard_process, True)
        assert not ready_stage.check_defeat(0)

    def test_check_defeat_returns_true_when_priority_process_terminated(self, ready_stage):
        process_manager = ready_stage.process_manager
        priority_process = next(
            slot.process for slot in process_manager.process_slots
            if slot.process is not None and slot.process.type == ProcessType.PRIORITY
        )
        process_manager.terminate_process(priority_process, True)
        assert ready_stage.check_defeat(0) == (True, 'The user killed a priority process.')

    def test_on_victory_shows_victory_dialog(self, stage):
        assert stage.modal is None

        stage.on_victory()

        assert isinstance(stage.modal, StoryStageResultDialog)
        assert stage.modal.is_victory is True
        assert stage.modal.reason is None
        assert stage.modal.stage_name == 'Stage 1: 1998'
        assert stage.modal.score == 0
        assert stage.modal.uptime == '0:00:00'

    def test_on_defeat_shows_defeat_dialog_with_reason(self, stage):
        assert stage.modal is None

        stage.on_defeat('The user killed a priority process.')

        assert isinstance(stage.modal, StoryStageResultDialog)
        assert stage.modal.is_victory is False
        assert stage.modal.reason == 'The user killed a priority process.'
        assert stage.modal.stage_name == 'Stage 1: 1998'
        assert stage.modal.score == 0
        assert stage.modal.uptime == '0:00:00'
