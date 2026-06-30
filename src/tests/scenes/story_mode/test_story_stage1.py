import pytest

from constants import ONE_MINUTE
from scenes.story_mode.story_stage1 import StoryStage1


class TestStoryStage1:
    @pytest.fixture
    def stage(self, scene_manager):
        stage = StoryStage1()
        stage.scene_manager = scene_manager
        stage.setup()
        return stage

    def test_check_victory_returns_false_before_five_minutes(self, stage):
        assert not stage.check_victory(5 * ONE_MINUTE - 1)

    def test_check_victory_returns_true_at_five_minutes(self, stage):
        assert stage.check_victory(5 * ONE_MINUTE)

    def test_check_victory_returns_true_after_five_minutes(self, stage):
        assert stage.check_victory(5 * ONE_MINUTE + 1)
