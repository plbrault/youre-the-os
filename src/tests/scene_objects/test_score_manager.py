import pytest

from config.stage_config import StageConfig
from scene_objects.score_manager import ScoreManager


class StubProcessManager:
    def __init__(self):
        self.stats = {
            'alive_process_count': 0,
            'alive_process_count_by_starvation_level': [0, 0, 0, 0, 0, 0],
            'active_process_count': 0,
            'active_process_count_by_starvation_level': [0, 0, 0, 0, 0, 0],
            'blocked_active_process_count': 0,
            'io_event_count': 0,
            'io_wasted_action_count': 0,
            'gracefully_terminated_process_count': 0,
            'user_terminated_process_count': 0,
        }

    def get_current_stats(self):
        return dict(self.stats)


class StubStage:
    def __init__(self):
        self.process_manager = StubProcessManager()


class TestScoreManager:
    @pytest.fixture
    def stub_stage(self):
        return StubStage()

    @pytest.fixture
    def score_manager(self, stub_stage):
        return ScoreManager(stub_stage)

    @pytest.fixture
    def score_manager_with_five_thousand_points(self, stub_stage, score_manager):
        # Award 1000 points per interval through five graceful terminations
        for i in range(1, 6):
            stub_stage.process_manager.stats['gracefully_terminated_process_count'] = i
            score_manager.update(i * 100, [])
        return score_manager

    def test_score_starts_at_zero(self, score_manager):
        assert score_manager.score == 0

    def test_one_graceful_termination_awards_one_thousand_points(self, stub_stage, score_manager):
        stub_stage.process_manager.stats['gracefully_terminated_process_count'] = 1
        score_manager.update(100, [])

        assert score_manager.score == 1000

    def test_two_graceful_terminations_in_one_interval_award_two_thousand_points(
            self, stub_stage, score_manager):
        stub_stage.process_manager.stats['gracefully_terminated_process_count'] = 2
        score_manager.update(100, [])

        assert score_manager.score == 2000

    def test_three_graceful_terminations_in_one_interval_award_three_thousand_points(
            self, stub_stage, score_manager):
        stub_stage.process_manager.stats['gracefully_terminated_process_count'] = 3
        score_manager.update(100, [])

        assert score_manager.score == 3000

    def test_graceful_terminations_in_separate_intervals_award_same_points(
            self, stub_stage, score_manager):
        stub_stage.process_manager.stats['gracefully_terminated_process_count'] = 1
        score_manager.update(100, [])
        stub_stage.process_manager.stats['gracefully_terminated_process_count'] = 2
        score_manager.update(200, [])

        assert score_manager.score == 2000

    def test_one_user_termination_deducts_one_thousand_points(
            self, stub_stage, score_manager_with_five_thousand_points):
        stub_stage.process_manager.stats['user_terminated_process_count'] = 1
        score_manager_with_five_thousand_points.update(600, [])

        assert score_manager_with_five_thousand_points.score == 4000

    def test_two_user_terminations_in_one_interval_deduct_two_thousand_points(
            self, stub_stage, score_manager_with_five_thousand_points):
        stub_stage.process_manager.stats['user_terminated_process_count'] = 2
        score_manager_with_five_thousand_points.update(600, [])

        assert score_manager_with_five_thousand_points.score == 3000

    def test_user_terminations_in_separate_intervals_deduct_same_points(
            self, stub_stage, score_manager_with_five_thousand_points):
        stub_stage.process_manager.stats['user_terminated_process_count'] = 1
        score_manager_with_five_thousand_points.update(600, [])
        stub_stage.process_manager.stats['user_terminated_process_count'] = 2
        score_manager_with_five_thousand_points.update(700, [])

        assert score_manager_with_five_thousand_points.score == 3000

    def test_user_terminations_penalty_does_not_bring_score_below_zero(
            self, stub_stage, score_manager):
        stub_stage.process_manager.stats['gracefully_terminated_process_count'] = 1
        score_manager.update(100, [])
        stub_stage.process_manager.stats['user_terminated_process_count'] = 2
        score_manager.update(200, [])

        assert score_manager.score == 0

    def test_two_processes_terminating_gracefully_in_same_frame_award_two_thousand_points(
            self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            num_processes_at_startup=2,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=1,
        ))
        # Processes at startup are created 50 ms apart
        stage.update(50, [])
        stage.update(100, [])
        stage.process_manager.get_process(1).use_cpu()
        stage.process_manager.get_process(2).use_cpu()
        score_manager = ScoreManager(stage)

        # Both processes terminate once they have been running for one second
        stage.update(1100, [])
        score_manager.update(1100, [])

        assert stage.process_manager.get_current_stats()['gracefully_terminated_process_count'] == 2
        assert score_manager.score == 2000
