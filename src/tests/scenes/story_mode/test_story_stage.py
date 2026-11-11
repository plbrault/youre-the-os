import pytest

from constants import ONE_MINUTE, ONE_SECOND
from config.cpu_config import CpuConfig
from config.stage_config import StageConfig
from engine.game_manager import GameManager
from engine.random import Random
from scene_objects.process import ProcessType
from scene_objects.stage_intro_dialog import (
    KilledProcessBadge, Section, StageIntroDialog, TimerBadge,
)
from scenes.story_mode.story_stage import (
    MaxTerminatedProcessVictoryCondition,
    SurvivalVictoryCondition,
    StoryStage,
    TimeVictoryCondition,
    VictoryCondition,
)


_STAGE_CONFIG = StageConfig(
    cpu_config=CpuConfig(num_cores=1),
    num_processes_at_startup=4,
    max_processes_terminated_by_user=4,
    high_priority_process_probability=0,
)

_INTRO_SECTIONS = (Section('Desktop PC', ('Single-Core CPU',)),)
_VICTORY_CONDITIONS = (
    SurvivalVictoryCondition(
        minutes=3,
        max_terminated_process=4,
        max_terminated_high_priority_process=0),
)

_INTRO_ITEMS = (
    'Survive 3 minutes with less than 4 user ragequits',
    'Do not let the user kill a high-priority process',
)
_INTRO_BADGES = (
    TimerBadge(3),
    KilledProcessBadge('<4'),
    KilledProcessBadge('0', is_high_priority=True),
)


class SampleStoryStage(StoryStage):

    stage_name = 'Test Story Stage'
    victory_conditions = _VICTORY_CONDITIONS
    intro_sections = _INTRO_SECTIONS

    def __init__(self):
        super().__init__(_STAGE_CONFIG)


class StubUptimeManager:

    def __init__(self, uptime_ms):
        self.uptime_ms = uptime_ms


class StubProcessManager:

    def __init__(self, processes):
        self.user_terminated_processes = list(processes)

    @property
    def user_terminated_process_count(self):
        return len(self.user_terminated_processes)


class StubStage:

    def __init__(self, uptime_ms=0, user_terminated_processes=()):
        self.uptime_manager = StubUptimeManager(uptime_ms)
        self.process_manager = StubProcessManager(user_terminated_processes)


class StubProcess:

    def __init__(self, process_type):
        self.type = process_type


def _advance_uptime_to(stage, uptime_ms):
    stage.uptime_manager.update(0, [])
    for time in range(ONE_SECOND, uptime_ms + 1, ONE_SECOND):
        stage.uptime_manager.update(time, [])


class TestVictoryCondition:
    def test_check_victory_defaults_to_false(self):
        assert not VictoryCondition().check_victory(StubStage())

    def test_check_defeat_defaults_to_none(self):
        assert VictoryCondition().check_defeat(StubStage()) is None

    def test_intro_items_default_to_empty(self):
        assert VictoryCondition().intro_items == ()

    def test_badges_default_to_empty(self):
        assert VictoryCondition().badges == ()


class TestTimeVictoryCondition:
    def test_check_victory_returns_false_before_victory_time(self):
        condition = TimeVictoryCondition(7)
        stub = StubStage(7 * ONE_MINUTE - 1)
        assert not condition.check_victory(stub)

    def test_check_victory_returns_true_at_victory_time(self):
        condition = TimeVictoryCondition(7)
        stub = StubStage(7 * ONE_MINUTE)
        assert condition.check_victory(stub)

    def test_check_victory_returns_true_after_victory_time(self):
        condition = TimeVictoryCondition(7)
        stub = StubStage(7 * ONE_MINUTE + 1)
        assert condition.check_victory(stub)

    def test_intro_items(self):
        assert TimeVictoryCondition(7).intro_items == ('Survive 7 minutes',)

    def test_badges(self):
        assert TimeVictoryCondition(7).badges == (TimerBadge(7),)


class TestMaxTerminatedProcessVictoryCondition:
    def test_check_defeat_returns_none_without_terminated_process(self):
        condition = MaxTerminatedProcessVictoryCondition(2)
        stub = StubStage(user_terminated_processes=())
        assert condition.check_defeat(stub) is None

    def test_check_defeat_returns_none_below_limit(self):
        condition = MaxTerminatedProcessVictoryCondition(2)
        stub = StubStage(user_terminated_processes=[
            StubProcess(ProcessType.STANDARD),
        ])
        assert condition.check_defeat(stub) is None

    def test_check_defeat_returns_ragequit_reason_at_limit(self):
        condition = MaxTerminatedProcessVictoryCondition(2)
        stub = StubStage(user_terminated_processes=[
            StubProcess(ProcessType.STANDARD),
            StubProcess(ProcessType.STANDARD),
        ])
        assert condition.check_defeat(stub) == 'Too many user ragequits.'

    def test_check_defeat_returns_priority_reason_when_high_priority_process_terminated(self):
        condition = MaxTerminatedProcessVictoryCondition(
            max_terminated_process=2, max_terminated_high_priority_process=0)
        stub = StubStage(user_terminated_processes=[
            StubProcess(ProcessType.HIGH_PRIORITY),
        ])
        assert condition.check_defeat(stub) == 'The user killed a high-priority process.'

    def test_check_defeat_returns_too_many_high_priority_reason_when_kills_allowed(self):
        condition = MaxTerminatedProcessVictoryCondition(
            max_terminated_process=100, max_terminated_high_priority_process=1)
        stub = StubStage(user_terminated_processes=[
            StubProcess(ProcessType.HIGH_PRIORITY),
            StubProcess(ProcessType.HIGH_PRIORITY),
        ])
        assert condition.check_defeat(stub) == 'The user killed too many high-priority processes.'

    def test_check_defeat_allows_high_priority_process_by_default(self):
        condition = MaxTerminatedProcessVictoryCondition(100)
        stub = StubStage(user_terminated_processes=[
            StubProcess(ProcessType.HIGH_PRIORITY),
        ])
        assert condition.check_defeat(stub) is None

    def test_intro_items(self):
        condition = MaxTerminatedProcessVictoryCondition(
            max_terminated_process=2, max_terminated_high_priority_process=0)
        assert condition.intro_items == (
            'less than 2 user ragequits',
            'Do not let the user kill a high-priority process',
        )

    def test_intro_items_have_no_high_priority_line_by_default(self):
        condition = MaxTerminatedProcessVictoryCondition(2)
        assert condition.intro_items == ('less than 2 user ragequits',)

    def test_intro_items_omits_high_priority_line_when_allowed(self):
        condition = MaxTerminatedProcessVictoryCondition(
            max_terminated_process=2, max_terminated_high_priority_process=1)
        assert condition.intro_items == ('less than 2 user ragequits',)

    def test_badges(self):
        condition = MaxTerminatedProcessVictoryCondition(
            max_terminated_process=2, max_terminated_high_priority_process=0)
        assert condition.badges == (
            KilledProcessBadge('<2'),
            KilledProcessBadge('0', is_high_priority=True),
        )

    def test_badges_have_no_high_priority_badge_by_default(self):
        condition = MaxTerminatedProcessVictoryCondition(2)
        assert condition.badges == (KilledProcessBadge('<2'),)

    def test_badges_with_nonzero_high_priority_limit(self):
        condition = MaxTerminatedProcessVictoryCondition(
            max_terminated_process=2, max_terminated_high_priority_process=1)
        assert condition.badges == (
            KilledProcessBadge('<2'),
            KilledProcessBadge('<2', is_high_priority=True),
        )


class TestSurvivalVictoryCondition:
    def test_check_victory(self):
        condition = SurvivalVictoryCondition(minutes=3, max_terminated_process=1)
        stub = StubStage(3 * ONE_MINUTE - 1)
        assert not condition.check_victory(stub)

        condition = SurvivalVictoryCondition(minutes=3, max_terminated_process=1)
        stub = StubStage(3 * ONE_MINUTE)
        assert condition.check_victory(stub)

    def test_check_defeat_high_priority_reason_takes_precedence(self):
        condition = SurvivalVictoryCondition(
            minutes=3, max_terminated_process=1, max_terminated_high_priority_process=0)
        stub = StubStage(user_terminated_processes=[
            StubProcess(ProcessType.HIGH_PRIORITY),
            StubProcess(ProcessType.STANDARD),
        ])
        assert condition.check_defeat(stub) == 'The user killed a high-priority process.'

    def test_check_defeat_ragequit_reason(self):
        condition = SurvivalVictoryCondition(minutes=3, max_terminated_process=1)
        stub = StubStage(user_terminated_processes=[
            StubProcess(ProcessType.STANDARD),
        ])
        assert condition.check_defeat(stub) == 'Too many user ragequits.'

    def test_intro_items(self):
        condition = SurvivalVictoryCondition(
            minutes=6, max_terminated_process=5, max_terminated_high_priority_process=0)
        assert condition.intro_items == (
            'Survive 6 minutes with less than 5 user ragequits',
            'Do not let the user kill a high-priority process',
        )

    def test_intro_items_omit_high_priority_line_when_kills_allowed(self):
        condition = SurvivalVictoryCondition(
            minutes=3,
            max_terminated_process=100,
            max_terminated_high_priority_process=1)
        assert condition.intro_items == (
            'Survive 3 minutes with less than 100 user ragequits',
        )

    def test_badges(self):
        condition = SurvivalVictoryCondition(
            minutes=6, max_terminated_process=5, max_terminated_high_priority_process=0)
        assert condition.badges == (
            TimerBadge(6),
            KilledProcessBadge('<5'),
            KilledProcessBadge('0', is_high_priority=True),
        )


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

    def test_on_start_shows_intro_dialog_with_victory_conditions(self, stage):
        stage.on_start()

        assert isinstance(stage.active_modal, StageIntroDialog)
        assert stage.active_modal.title == 'Test Story Stage'
        assert stage.active_modal.sections == (*_INTRO_SECTIONS, Section(
            'Victory Conditions', _INTRO_ITEMS))
        assert stage.active_modal.badges == _INTRO_BADGES

    def test_on_start_builds_a_new_intro_dialog_each_time(self, stage):
        stage.on_start()
        first_modal = stage.active_modal

        stage.close_modal()
        stage.on_start()

        assert stage.active_modal is not first_modal
