import pytest

import pygame

import game_monitor
from constants import DEAD_STARVATION_LEVEL, ONE_SECOND, FRAMERATE
from engine.player_input import PlayerInput
from engine.player_input_type import PlayerInputType
from engine.game_manager import GameManager
from engine.modal import Modal
from engine.modal_view import ModalView
from engine.random import Random
from config.cpu_config import CpuConfig
from config.stage_config import StageConfig
from scene_objects.game_over_dialog import GameOverDialog
from scene_objects.hotkey_dialog import HotkeyDialog
from scene_objects.in_game_menu_dialog import InGameMenuDialog
from scene_objects.process import Process, ProcessState
from scene_objects.tooltip import Tooltip
from scenes.stage import Stage
from scenes.stage import StageState
from scenes.stage import StateEvent


class StubModalView(ModalView):
    def __init__(self):
        super().__init__()

    @property
    def width(self):
        return 200

    @property
    def height(self):
        return 100

    def draw_content(self, surface):
        pass


class StubModal(Modal):
    def __init__(self):
        super().__init__(StubModalView())


class MockStage(Stage):
    def __init__(self, victory_uptime=None, defeat_uptime=None,
                 defeat_reason='Defeat time reached', **kwargs):
        super().__init__(**kwargs)
        self.victory_uptime = victory_uptime
        self.defeat_uptime = defeat_uptime
        self.defeat_reason = defeat_reason
        self.on_start_call_count = 0
        self.on_victory_call_count = 0
        self.on_defeat_call_count = 0
        self.on_defeat_reasons = []

    def check_victory(self):
        if self.victory_uptime is not None:
            return self.uptime_manager.uptime_ms >= self.victory_uptime
        return False

    def check_defeat(self):
        if self.defeat_uptime is not None and \
                self.uptime_manager.uptime_ms >= self.defeat_uptime:
            if self.defeat_reason is None:
                return True
            return (True, self.defeat_reason)
        return False

    def on_start(self):
        self.on_start_call_count += 1

    def on_victory(self):
        self.on_victory_call_count += 1

    def on_defeat(self, reason=None):
        self.on_defeat_call_count += 1
        self.on_defeat_reasons.append(reason)


class MockStageWithStaleReason(Stage):
    """Stage whose check_defeat first returns (False, stale) then plain True.

    Used to verify that a non-defeating tuple from check_defeat does not leak
    its reason into a later defeating frame that returns a plain bool.
    """

    def __init__(self, stale_uptime, defeat_uptime, **kwargs):
        super().__init__(**kwargs)
        self._stale_uptime = stale_uptime
        self._defeat_uptime = defeat_uptime
        self._on_defeat_call_count = 0
        self._on_defeat_reasons = []

    @property
    def on_defeat_call_count(self):
        return self._on_defeat_call_count

    @property
    def on_defeat_reasons(self):
        return self._on_defeat_reasons

    def check_victory(self):
        return False

    def check_defeat(self):
        uptime = self.uptime_manager.uptime_ms
        if uptime >= self._defeat_uptime:
            return True
        if uptime >= self._stale_uptime:
            return (False, 'Stale reason')
        return False

    def on_start(self):
        pass

    def on_victory(self):
        pass

    def on_defeat(self, reason=None):
        self._on_defeat_call_count += 1
        self._on_defeat_reasons.append(reason)


class TestStageStateMachine:
    """Tests for the Stage state machine transitions and behavior per the design spec."""

    @pytest.fixture
    def mock_stage(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
        )
        stage.scene_manager = scene_manager
        stage.setup()
        return stage

    def test_initial_state_is_starting(self, mock_stage):
        assert mock_stage.state == StageState.STARTING

    def test_stage_state_accessible_via_class(self):
        assert Stage.StageState is StageState

    def test_stage_state_enum_members(self):
        member_names = [m.name for m in StageState]
        assert member_names == [
            'STARTING', 'PLAYING', 'AWAITING_VICTORY', 'AWAITING_DEFEAT',
            'VICTORY', 'DEFEAT', 'ENDED',
        ]

    def test_state_event_enum_members(self):
        member_names = [m.name for m in StateEvent]
        assert member_names == [
            'START', 'VICTORY_DETECTED', 'DEFEAT_DETECTED',
            'PROCESSES_SETTLED', 'DELAY_ELAPSED',
        ]

    def test_starting_to_playing_via_start(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        assert mock_stage.state == StageState.PLAYING

    def test_playing_to_awaiting_victory(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.VICTORY_DETECTED)
        assert mock_stage.state == StageState.AWAITING_VICTORY

    def test_playing_to_awaiting_defeat(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.DEFEAT_DETECTED)
        assert mock_stage.state == StageState.AWAITING_DEFEAT

    def test_awaiting_victory_to_victory(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.VICTORY_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        assert mock_stage.state == StageState.VICTORY

    def test_awaiting_defeat_to_defeat(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.DEFEAT_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        assert mock_stage.state == StageState.DEFEAT

    def test_victory_to_ended(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.VICTORY_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        mock_stage.apply_state_transition(StateEvent.DELAY_ELAPSED)
        assert mock_stage.state == StageState.ENDED

    def test_defeat_to_ended(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.DEFEAT_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        mock_stage.apply_state_transition(StateEvent.DELAY_ELAPSED)
        assert mock_stage.state == StageState.ENDED

    def test_starting_ignores_invalid_state_events(self, mock_stage):
        invalid_state_events = [
            StateEvent.VICTORY_DETECTED,
            StateEvent.DEFEAT_DETECTED,
            StateEvent.PROCESSES_SETTLED,
            StateEvent.DELAY_ELAPSED,
        ]
        for state_event in invalid_state_events:
            mock_stage.apply_state_transition(state_event)
            assert mock_stage.state == StageState.STARTING

    def test_playing_ignores_invalid_state_events(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        invalid_state_events = [
            StateEvent.START,
            StateEvent.PROCESSES_SETTLED,
            StateEvent.DELAY_ELAPSED,
        ]
        for state_event in invalid_state_events:
            mock_stage.apply_state_transition(state_event)
            assert mock_stage.state == StageState.PLAYING

    def test_awaiting_victory_ignores_invalid_state_events(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.VICTORY_DETECTED)
        invalid_state_events = [
            StateEvent.START,
            StateEvent.VICTORY_DETECTED,
            StateEvent.DEFEAT_DETECTED,
            StateEvent.DELAY_ELAPSED,
        ]
        for state_event in invalid_state_events:
            mock_stage.apply_state_transition(state_event)
            assert mock_stage.state == StageState.AWAITING_VICTORY

    def test_awaiting_defeat_ignores_invalid_state_events(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.DEFEAT_DETECTED)
        invalid_state_events = [
            StateEvent.START,
            StateEvent.VICTORY_DETECTED,
            StateEvent.DEFEAT_DETECTED,
            StateEvent.DELAY_ELAPSED,
        ]
        for state_event in invalid_state_events:
            mock_stage.apply_state_transition(state_event)
            assert mock_stage.state == StageState.AWAITING_DEFEAT

    def test_victory_ignores_invalid_state_events(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.VICTORY_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        invalid_state_events = [
            StateEvent.START,
            StateEvent.VICTORY_DETECTED,
            StateEvent.DEFEAT_DETECTED,
            StateEvent.PROCESSES_SETTLED,
        ]
        for state_event in invalid_state_events:
            mock_stage.apply_state_transition(state_event)
            assert mock_stage.state == StageState.VICTORY

    def test_defeat_ignores_invalid_state_events(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.DEFEAT_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        invalid_state_events = [
            StateEvent.START,
            StateEvent.VICTORY_DETECTED,
            StateEvent.DEFEAT_DETECTED,
            StateEvent.PROCESSES_SETTLED,
        ]
        for state_event in invalid_state_events:
            mock_stage.apply_state_transition(state_event)
            assert mock_stage.state == StageState.DEFEAT

    def test_ended_ignores_all_state_events(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.VICTORY_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        mock_stage.apply_state_transition(StateEvent.DELAY_ELAPSED)
        assert mock_stage.state == StageState.ENDED
        all_state_events = [
            StateEvent.START,
            StateEvent.VICTORY_DETECTED,
            StateEvent.DEFEAT_DETECTED,
            StateEvent.PROCESSES_SETTLED,
            StateEvent.DELAY_ELAPSED,
        ]
        for state_event in all_state_events:
            mock_stage.apply_state_transition(state_event)
            assert mock_stage.state == StageState.ENDED


class TestStageUpdateBehavior:
    """Tests for the Stage update() method behavior by state."""

    @pytest.fixture
    def mock_stage(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
        )
        stage.scene_manager = scene_manager
        stage.setup()
        return stage

    def test_starting_calls_on_start_on_first_update(self, mock_stage):
        assert mock_stage.state == StageState.STARTING
        mock_stage.update(0, [])
        assert mock_stage.on_start_call_count == 1

    def test_starting_calls_on_start_only_once(self, mock_stage):
        mock_stage.update(0, [])
        mock_stage.update(100, [])
        assert mock_stage.on_start_call_count == 1

    def test_starting_transitions_to_playing_on_first_update(self, mock_stage):
        mock_stage.update(0, [])
        assert mock_stage.state == StageState.PLAYING

    def test_starting_falls_through_to_playing(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            victory_uptime=0,
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(100, [])
        assert stage.state == StageState.AWAITING_VICTORY

    def test_playing_stays_in_playing_without_conditions(self, mock_stage):
        mock_stage.update(0, [])
        mock_stage.update(100, [])
        assert mock_stage.state == StageState.PLAYING
        mock_stage.update(200, [])
        assert mock_stage.state == StageState.PLAYING

    def test_playing_transitions_to_awaiting_victory_on_victory(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            victory_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])

        stage.update(1000, [])
        assert stage.state == StageState.AWAITING_VICTORY

    def test_playing_transitions_to_awaiting_defeat_on_defeat(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            defeat_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])

        stage.update(1000, [])
        assert stage.state == StageState.AWAITING_DEFEAT

    def test_playing_defeat_takes_precedence_over_victory(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            victory_uptime=1000,
            defeat_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])

        stage.update(1000, [])
        assert stage.state == StageState.AWAITING_DEFEAT

    def test_awaiting_victory_transitions_to_victory_when_processes_settle(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            victory_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(1000, [])

        assert stage.state == StageState.AWAITING_VICTORY

        stage.update(1001, [])
        assert stage.state == StageState.VICTORY

    def test_awaiting_defeat_transitions_to_defeat_when_processes_settle(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            defeat_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(1000, [])

        assert stage.state == StageState.AWAITING_DEFEAT

        stage.update(1001, [])
        assert stage.state == StageState.DEFEAT

    def test_victory_waits_one_second_before_on_victory(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            victory_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(1000, [])
        stage.update(1001, [])

        assert stage.state == StageState.VICTORY
        assert stage.on_victory_call_count == 0

        stage.update(1001 + ONE_SECOND, [])
        assert stage.on_victory_call_count == 0

        stage.update(1001 + ONE_SECOND + 1, [])
        assert stage.on_victory_call_count == 1
        assert stage.state == StageState.ENDED

    def test_defeat_waits_one_second_before_on_defeat(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            defeat_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(1000, [])
        stage.update(1001, [])

        assert stage.state == StageState.DEFEAT
        assert stage.on_defeat_call_count == 0

        stage.update(1001 + ONE_SECOND, [])
        assert stage.on_defeat_call_count == 0

        stage.update(1001 + ONE_SECOND + 1, [])
        assert stage.on_defeat_call_count == 1
        assert stage.state == StageState.ENDED

    def test_on_victory_called_only_once(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            victory_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(1000, [])
        stage.update(1001, [])
        stage.update(1001 + ONE_SECOND + 1, [])

        assert stage.on_victory_call_count == 1

        stage.update(1001 + ONE_SECOND + 2, [])
        stage.update(1001 + ONE_SECOND + 3, [])
        assert stage.on_victory_call_count == 1

    def test_on_defeat_called_only_once(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            defeat_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(1000, [])
        stage.update(1001, [])
        stage.update(1001 + ONE_SECOND + 1, [])

        assert stage.on_defeat_call_count == 1

        stage.update(1001 + ONE_SECOND + 2, [])
        stage.update(1001 + ONE_SECOND + 3, [])
        assert stage.on_defeat_call_count == 1

    def test_ended_state_does_nothing_on_update(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            victory_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(1000, [])
        stage.update(1001, [])
        stage.update(1001 + ONE_SECOND + 1, [])

        assert stage.state == StageState.ENDED
        assert stage.on_victory_call_count == 1

        stage.update(10000, [])
        assert stage.state == StageState.ENDED
        assert stage.on_victory_call_count == 1

    def test_stage_not_completed_when_neither_condition_met(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(100, [])
        assert not stage.stage_completed
        assert stage.on_victory_call_count == 0
        assert stage.on_defeat_call_count == 0

        stage.update(1000, [])
        assert not stage.stage_completed
        assert stage.on_victory_call_count == 0
        assert stage.on_defeat_call_count == 0

        stage.update(10000, [])
        assert not stage.stage_completed
        assert stage.on_victory_call_count == 0
        assert stage.on_defeat_call_count == 0

    def test_defeat_reason_from_tuple_check_defeat_passed_to_on_defeat(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            defeat_uptime=1000,
            defeat_reason='Defeat time reached',
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(0, [])
        stage.update(1000, [])
        stage.update(1001, [])
        assert stage.state == StageState.DEFEAT

        stage.update(1001 + ONE_SECOND + 1, [])
        assert stage.on_defeat_call_count == 1
        assert stage.on_defeat_reasons == ['Defeat time reached']

    def test_defeat_reason_is_none_when_check_defeat_returns_bool(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            defeat_uptime=1000,
            defeat_reason=None,
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(0, [])
        stage.update(1000, [])
        stage.update(1001, [])
        assert stage.state == StageState.DEFEAT

        stage.update(1001 + ONE_SECOND + 1, [])
        assert stage.on_defeat_call_count == 1
        assert stage.on_defeat_reasons == [None]

    def test_false_tuple_check_defeat_does_not_leak_reason_into_later_bool_defeat(
        self, scene_manager,
    ):
        stage = MockStageWithStaleReason(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            stale_uptime=1000,
            defeat_uptime=2000,
        )
        stage.scene_manager = scene_manager
        stage.setup()

        # Frame 0: no defeat, check_defeat returns False (default bool).
        stage.update(0, [])
        assert stage.state == StageState.PLAYING
        # Frame 1: check_defeat returns (False, 'Stale reason') -> not defeated.
        stage.update(1000, [])
        assert stage.state == StageState.PLAYING
        # Frame 2: check_defeat returns plain True -> defeated, reason should be None.
        stage.update(2000, [])
        stage.update(2001, [])
        assert stage.state == StageState.DEFEAT

        stage.update(2001 + ONE_SECOND + 1, [])
        assert stage.on_defeat_call_count == 1
        assert stage.on_defeat_reasons == [None]


class TestStageCompletedProperty:
    """Tests for the stage_completed property based on the state machine."""

    @pytest.fixture
    def mock_stage(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
        )
        stage.scene_manager = scene_manager
        stage.setup()
        return stage

    def test_stage_completed_false_in_starting(self, mock_stage):
        assert mock_stage.state == StageState.STARTING
        assert not mock_stage.stage_completed

    def test_stage_completed_false_in_playing(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        assert mock_stage.state == StageState.PLAYING
        assert not mock_stage.stage_completed

    def test_stage_completed_false_in_awaiting_victory(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.VICTORY_DETECTED)
        assert mock_stage.state == StageState.AWAITING_VICTORY
        assert not mock_stage.stage_completed

    def test_stage_completed_false_in_awaiting_defeat(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.DEFEAT_DETECTED)
        assert mock_stage.state == StageState.AWAITING_DEFEAT
        assert not mock_stage.stage_completed

    def test_stage_completed_true_in_victory(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.VICTORY_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        assert mock_stage.state == StageState.VICTORY
        assert mock_stage.stage_completed

    def test_stage_completed_true_in_defeat(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.DEFEAT_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        assert mock_stage.state == StageState.DEFEAT
        assert mock_stage.stage_completed

    def test_stage_completed_true_in_ended(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.VICTORY_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        mock_stage.apply_state_transition(StateEvent.DELAY_ELAPSED)
        assert mock_stage.state == StageState.ENDED
        assert mock_stage.stage_completed


class TestStageHooks:
    """Tests for on_start, on_victory, and on_defeat hook methods."""

    def test_on_start_default_is_no_op(self, scene_manager):
        stage = Stage('Test', StageConfig(num_processes_at_startup=0, new_process_probability=0))
        stage.scene_manager = scene_manager
        stage.setup()
        stage.on_start()

    def test_on_victory_default_is_no_op(self, scene_manager):
        stage = Stage('Test', StageConfig(num_processes_at_startup=0, new_process_probability=0))
        stage.scene_manager = scene_manager
        stage.setup()

        assert stage.active_modal is None
        stage.on_victory()
        assert stage.active_modal is None

    def test_on_defeat_default_shows_game_over_dialog(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=4,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
        ))

        assert stage.active_modal is None
        stage.on_defeat()
        assert isinstance(stage.active_modal, GameOverDialog)

    def test_reset_resets_state_to_starting(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            victory_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(0, [])
        stage.update(1000, [])
        assert stage.state == StageState.AWAITING_VICTORY

        stage.reset()
        assert stage.state == StageState.STARTING

    def test_reset_allows_on_start_to_fire_again(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            victory_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(0, [])
        assert stage.on_start_call_count == 1

        stage.reset()

        stage.update(0, [])
        assert stage.on_start_call_count == 2

    def test_reset_allows_hooks_to_fire_again(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0, new_process_probability=0),
            victory_uptime=1000,
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(0, [])
        stage.update(1000, [])
        stage.update(1001, [])
        stage.update(1001 + ONE_SECOND + 1, [])
        assert stage.on_victory_call_count == 1

        stage.reset()

        stage.update(0, [])
        stage.update(1000, [])
        stage.update(1001, [])
        stage.update(1001 + ONE_SECOND + 1, [])
        assert stage.on_victory_call_count == 2


class TestStage:
    @pytest.fixture
    def stage_custom_config(self, scene_manager, monkeypatch):
        def create_stage(custom_config):
            monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

            stage = Stage('Test Stage', custom_config)
            stage.scene_manager = scene_manager
            stage.setup()
            process_manager = stage.process_manager

            time = 0.0
            process_count = 0
            process_in_motion = 0
            iteration_count = 0

            while (
                (
                    process_count < custom_config.num_processes_at_startup
                    or process_in_motion > 0
                )
                and iteration_count < 100000
            ):
                iteration_count += 1
                process_manager.update(int(time), [])
                time += ONE_SECOND / GameManager.fps

                used_process_slots = [
                    process_slot for process_slot in process_manager.process_slots
                    if process_slot.process is not None
                ]
                process_count = len(used_process_slots)
                process_in_motion = len([
                    process_slot for process_slot in used_process_slots
                    if process_slot.process.is_in_motion
                ])

            monkeypatch.setattr(Random, 'get_number', Random.get_number)

            return stage
        return create_stage

    def test_setup_initializes_scene_objects(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=4,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
        ))

        assert stage.process_manager is not None
        assert stage.page_manager is not None
        assert stage.uptime_manager is not None

    def test_io_events_tooltip_in_front_layer(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=0,
            new_process_probability=0,
        ))

        tooltip = next(
            child for child in stage.children if isinstance(child, Tooltip))

        assert tooltip.text == 'Click here to unblock processes'
        assert stage.children[-1] is tooltip

    def test_io_events_tooltip_shows_after_30_seconds_of_blinking(
            self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=0,
            new_process_probability=0,
        ))
        tooltip = next(
            child for child in stage.children if isinstance(child, Tooltip))
        assert tooltip.visible == False

        io_queue = stage.process_manager.io_queue
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)
        io_queue.wait_for_io_event(0, lambda: None, lambda: None)
        io_queue.update(1000, [])
        monkeypatch.setattr(Random, 'get_number', Random.get_number)

        stage.update(30999, [])
        assert tooltip.visible == False

        stage.update(31000, [])
        assert tooltip.visible == True

        io_queue.handle_player_action()

        stage.update(31250, [])
        assert tooltip.visible == True

        stage.update(31375, [])
        assert tooltip.opacity == 0.5

        stage.update(31500, [])
        assert tooltip.visible == False
        assert tooltip.opacity == 0

    def test_stage_completed_initially_false(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=4,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
        ))

        assert not stage.stage_completed

    def test_name_property(self):
        stage = Stage('My Stage', StageConfig())
        assert stage.name == 'My Stage'
        stage.name = 'Renamed'
        assert stage.name == 'Renamed'

    def test_standalone_property(self):
        stage = Stage('Test', StageConfig(), standalone=True)
        assert stage.standalone
        stage.standalone = False
        assert not stage.standalone

    def test_stage_completed(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=10,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
            time_ms_to_show_sort_button=0,
        ))

        process_manager = stage.process_manager

        for i in range(1, 11):
            process = process_manager.get_process(i)
            time = 0
            while process.starvation_level < DEAD_STARVATION_LEVEL:
                process.update(time, [])
                time += ONE_SECOND

        assert not stage.stage_completed

        process_in_motion = True
        time = 1000
        while process_in_motion:
            process_manager.update(time, [])
            process_in_motion = False
            for child in process_manager.children:
                if isinstance(child, Process) and child.is_in_motion:
                    process_in_motion = True
                    break
            time += ONE_SECOND / FRAMERATE

        stage.update(time, [])
        stage.update(time + ONE_SECOND // FRAMERATE, [])

        assert stage.stage_completed

    def test_stage_completed_does_not_trigger_before_max_terminated(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=10,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
            time_ms_to_show_sort_button=0,
        ))

        process_manager = stage.process_manager

        for i in range(1, 6):
            process = process_manager.get_process(i)
            time = 0
            while process.starvation_level < DEAD_STARVATION_LEVEL:
                process.update(time, [])
                time += ONE_SECOND

        process_in_motion = True
        time = 1000
        while process_in_motion:
            process_manager.update(time, [])
            process_in_motion = False
            for child in process_manager.children:
                if isinstance(child, Process) and child.is_in_motion:
                    process_in_motion = True
                    break
            time += ONE_SECOND / FRAMERATE

        stage.update(time, [])

        assert not stage.stage_completed

    def test_stage_completed_does_not_trigger_while_processes_in_motion(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=10,
            max_processes_terminated_by_user=1,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
            time_ms_to_show_sort_button=0,
        ))

        process_manager = stage.process_manager
        process = process_manager.get_process(1)
        time = 0
        while process.starvation_level < DEAD_STARVATION_LEVEL:
            process.update(time, [])
            time += ONE_SECOND

        assert process_manager.user_terminated_process_count == 1

        any_in_motion = any(
            isinstance(so, Process) and so.is_in_motion
            for so in process_manager.children
        )
        if any_in_motion:
            stage.update(time, [])
            assert not stage.stage_completed

    def test_reset_closes_active_modal(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=4,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
        ))

        stage.open_modal(StubModal())

        stage.reset()

        assert stage.active_modal is None

    def test_reset_routes_player_inputs_to_scene_objects(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=4,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
        ))

        stage.open_modal(StubModal())
        stage.reset()

        update_received = False
        original_update = stage.process_manager.update

        def spy_update(current_time, player_inputs):
            nonlocal update_received
            update_received = True
            original_update(current_time, player_inputs)

        stage.process_manager.update = spy_update
        stage.update(0, [])

        assert update_received

    def test_stage_renders_scene_objects(self, stage, monkeypatch):
        # pygame.display.flip requires an initialized video system,
        # which is not needed for exercising the views' draw calls.
        monkeypatch.setattr(pygame.display, 'flip', lambda: None)
        stage.update(0, [])
        stage.render()

    def test_stage_completed_via_victory(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(
                num_processes_at_startup=0, new_process_probability=0
            ),
            victory_uptime=1000
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(0, [])
        assert not stage.stage_completed
        assert stage.on_victory_call_count == 0

        stage.update(1000, [])
        assert not stage.stage_completed
        assert stage.on_victory_call_count == 0

        stage.update(1001, [])
        assert stage.stage_completed
        assert stage.on_victory_call_count == 0

        stage.update(1001 + ONE_SECOND, [])
        assert stage.on_victory_call_count == 0

        stage.update(1001 + ONE_SECOND + 1, [])
        assert stage.on_victory_call_count == 1

        stage.update(1001 + ONE_SECOND + 2, [])
        assert stage.on_victory_call_count == 1

    def test_stage_completed_via_defeat(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(
                num_processes_at_startup=0, new_process_probability=0
            ),
            defeat_uptime=1000
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(0, [])
        assert not stage.stage_completed
        assert stage.on_defeat_call_count == 0

        stage.update(1000, [])
        assert not stage.stage_completed
        assert stage.on_defeat_call_count == 0

        stage.update(1001, [])
        assert stage.stage_completed
        assert stage.on_defeat_call_count == 0

        stage.update(1001 + ONE_SECOND, [])
        assert stage.on_defeat_call_count == 0

        stage.update(1001 + ONE_SECOND + 1, [])
        assert stage.on_defeat_call_count == 1

        stage.update(1001 + ONE_SECOND + 2, [])
        assert stage.on_defeat_call_count == 1

    def test_stage_completion_waits_for_processes_to_stop(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=1),
            victory_uptime=0
        )
        stage.scene_manager = scene_manager
        stage.setup()

        process_manager = stage.process_manager

        stage.update(0, [])

        any_in_motion = True
        time = 600
        while any_in_motion:
            stage.update(int(time), [])
            any_in_motion = False
            for child in process_manager.children:
                if isinstance(child, Process) and child.is_in_motion:
                    any_in_motion = True
                    break
            time += ONE_SECOND / FRAMERATE

        assert stage.stage_completed
        assert stage.on_victory_call_count == 0

        stage.update(int(time) + ONE_SECOND + 1, [])
        assert stage.on_victory_call_count == 1


class TestStageGameMonitorEvents:
    @pytest.fixture
    def stage_config(self):
        return StageConfig(
            num_processes_at_startup=1,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
            max_pages_per_process=1,
        )

    @pytest.fixture
    def script(self):
        # Automation script that moves every newly created process to a CPU
        return compile(
            "def scheduler(events):\n"
            "    return [\n"
            "        {'type': 'process', 'pid': event.pid}\n"
            "        for event in events if event.etype == 'PROC_NEW'\n"
            "    ]\n",
            'test_script.py',
            'exec'
        )

    def test_update_without_script_drains_notifications_emitted_before_the_frame(
            self, stage_custom_config, stage_config):
        stage = stage_custom_config(stage_config)
        game_monitor.clear_notifications()
        game_monitor.notify_process_new(99)

        # The first process at startup is created 50 ms after setup
        stage.update(50, [])

        assert [n.pid for n in game_monitor.get_notifications() if n.etype == 'PROC_NEW'] == [1]

    def test_update_without_script_retains_only_current_frame_notifications(
            self, stage_custom_config, stage_config):
        stage = stage_custom_config(stage_config)
        game_monitor.clear_notifications()

        stage.update(50, [])
        stage.process_manager.get_process(1).use_cpu()
        for time in range(ONE_SECOND, 30 * ONE_SECOND + 1, ONE_SECOND):
            stage.update(time, [])
        notifications_after_30_seconds = len(game_monitor.get_notifications())
        for time in range(31 * ONE_SECOND, 60 * ONE_SECOND + 1, ONE_SECOND):
            stage.update(time, [])
        notifications_after_60_seconds = len(game_monitor.get_notifications())

        # A happy running process emits one starvation notification per second,
        # and only the notification of the current frame should be retained
        assert notifications_after_30_seconds == 1
        assert notifications_after_60_seconds == 1

    def test_reset_clears_notifications_of_previous_session(self, stage_custom_config, stage_config):
        stage = stage_custom_config(stage_config)
        game_monitor.clear_notifications()

        stage.update(50, [])
        stage.process_manager.get_process(1).use_cpu()
        for time in range(ONE_SECOND, 10 * ONE_SECOND + 1, ONE_SECOND):
            stage.update(time, [])

        stage.reset()

        assert len(game_monitor.get_notifications()) == 0

    def test_update_with_script_delivers_each_notification_once(self, scene_manager, stage_config, script):
        stage = Stage('Test Stage', stage_config, script=script)
        stage.scene_manager = scene_manager
        game_monitor.clear_notifications()
        stage.setup()

        # Process 1 is created on the first update, and the script receives
        # its PROC_NEW notification on the next update
        stage.update(50, [])
        stage.update(100, [])

        assert stage.process_manager.get_process(1).has_cpu == True

        # The PROC_NEW notification must not be delivered again, otherwise the script
        # would toggle the process off its CPU
        stage.update(150, [])
        stage.update(200, [])

        assert stage.process_manager.get_process(1).has_cpu == True


class TestInGameMenu:
    """Tests for the in-game menu modal and its Hotkeys button."""

    @pytest.fixture
    def stage(self, stage_custom_config, scene_manager):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=4,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
        ))
        scene_manager.start_scene(stage, 0)
        return stage

    @staticmethod
    def _key_up_player_input(key):
        return PlayerInput(PlayerInputType.KEY_UP, {'key': key})

    @staticmethod
    def _click_on_player_input(scene_object):
        center = (
            scene_object.view.x + scene_object.view.width / 2,
            scene_object.view.y + scene_object.view.height / 2,
        )
        return PlayerInput(PlayerInputType.MOUSE_LEFT_CLICK, {'position': center})

    def test_opening_in_game_menu_opens_menu_dialog_and_pushes_its_context(
            self, stage, scene_manager):
        scene_manager.update(0, [self._key_up_player_input('escape')])

        assert isinstance(stage.active_modal, InGameMenuDialog)
        assert scene_manager.get_top_context() is stage.active_modal

    def test_hotkeys_button_opens_hotkey_dialog_on_top_of_menu(
            self, stage, scene_manager):
        scene_manager.update(0, [self._key_up_player_input('escape')])
        in_game_menu = stage.active_modal
        scene_manager.update(33, [self._click_on_player_input(in_game_menu.hotkeys_button)])

        assert isinstance(stage.active_modal, HotkeyDialog)
        assert scene_manager.get_top_context() is stage.active_modal

    def test_closing_hotkey_dialog_returns_to_menu(
            self, stage, scene_manager):
        scene_manager.update(0, [self._key_up_player_input('escape')])
        in_game_menu = stage.active_modal
        scene_manager.update(33, [self._click_on_player_input(in_game_menu.hotkeys_button)])
        hotkey_dialog = stage.active_modal
        scene_manager.update(66, [self._click_on_player_input(hotkey_dialog.close_button)])

        assert stage.active_modal is in_game_menu
        assert scene_manager.get_top_context() is in_game_menu


class TestStageConfigValidation:
    """Tests for the validation that the stage config can never occupy every page slot."""

    @pytest.fixture
    def stage_factory(self, scene_manager):
        def create_stage(stage_config):
            stage = Stage('Test Stage', stage_config)
            stage.scene_manager = scene_manager
            return stage
        return create_stage

    def test_setup_accepts_default_config(self, stage_factory):
        # The default config allows up to 42 * 4 = 168 pages at the same
        # time (42 page holders counting lingering processes), and there
        # are 16 * 11 = 176 page slots, so at least one slot always
        # remains free for page swaps
        stage = stage_factory(StageConfig(
            num_processes_at_startup=0,
            new_process_probability=0))

        stage.setup()

    def test_setup_rejects_config_that_could_occupy_every_page_slot(self, stage_factory):
        # The default CPU has 4 threads, so the bound accounts for
        # min(22 + 4, 42) = 26 page holders, each with up to 8 pages:
        # 26 * 8 = 208 pages, which is more than the 176 page slots
        stage = stage_factory(StageConfig(
            max_processes=22,
            max_pages_per_process=8,
            num_processes_at_startup=0,
            new_process_probability=0))

        with pytest.raises(ValueError) as exc_info:
            stage.setup()

        assert str(exc_info.value) == (
            'Stage config can generate up to 208 pages at the same time, '
            'but there are only 176 page slots; at least one slot '
            'must remain free for page swaps.')

    def test_setup_rejects_config_with_a_lingering_process_overflowing_the_page_slots(
            self, stage_factory):
        # 25 * 7 = 175 pages fits, but just one lingering process holding
        # its pages (min(25 + 4, 42) = 29 page holders in total) can fill
        # every page slot: 29 * 7 = 203 pages
        stage = stage_factory(StageConfig(
            max_processes=25,
            max_pages_per_process=7,
            num_processes_at_startup=0,
            new_process_probability=0))

        with pytest.raises(ValueError) as exc_info:
            stage.setup()

        assert str(exc_info.value) == (
            'Stage config can generate up to 203 pages at the same time, '
            'but there are only 176 page slots; at least one slot '
            'must remain free for page swaps.')

    def test_setup_accepts_config_leaving_exactly_one_page_slot_free(self, stage_factory):
        # The default CPU has 4 threads, so min(21 + 4, 42) = 25 page
        # holders, each of which can hold up to 7 pages: 25 * 7 = 175
        # pages at the same time, and 176 page slots, so exactly one
        # slot always remains free for page swaps
        stage = stage_factory(StageConfig(
            max_processes=21,
            max_pages_per_process=7,
            num_processes_at_startup=0,
            new_process_probability=0))

        stage.setup()

    def test_setup_rejects_config_generating_more_pages_than_page_slots(self, stage_factory):
        # 42 * 5 = 210 pages at the same time, but only 176 page slots
        stage = stage_factory(StageConfig(
            max_pages_per_process=5,
            num_processes_at_startup=0,
            new_process_probability=0))

        with pytest.raises(ValueError) as exc_info:
            stage.setup()

        assert str(exc_info.value) == (
            'Stage config can generate up to 210 pages at the same time, '
            'but there are only 176 page slots; at least one slot '
            'must remain free for page swaps.')

    def test_setup_rejects_config_when_more_threads_overflow_the_page_slots(
            self, stage_factory):
        # The same config as the exact one-slot-free boundary test except
        # for the CPU: 8 threads instead of 4 makes the bound
        # min(21 + 8, 42) = 29 page holders, and 29 * 7 = 203 pages,
        # which is more than the 176 page slots
        stage = stage_factory(StageConfig(
            cpu_config=CpuConfig(num_cores=8),
            max_processes=21,
            max_pages_per_process=7,
            num_processes_at_startup=0,
            new_process_probability=0))

        with pytest.raises(ValueError) as exc_info:
            stage.setup()

        assert str(exc_info.value) == (
            'Stage config can generate up to 203 pages at the same time, '
            'but there are only 176 page slots; at least one slot '
            'must remain free for page swaps.')

    def test_setup_ignores_min_processes_thresholds_when_bounding_processes(
            self, stage_factory):
        # Every process creation branch is bounded by max_processes, so the
        # min processes threshold of 42 can never allow more than
        # 2 * 5 = 10 pages at the same time, and there are 176 page slots
        stage = stage_factory(StageConfig(
            max_processes=2,
            max_pages_per_process=5,
            min_processes_at_times_ms=[(0, 42)],
            num_processes_at_startup=0,
            new_process_probability=0))

        stage.setup()

    def test_setup_rejects_config_allowing_more_processes_than_process_slots(
            self, stage_factory):
        # 60 processes, but there are only 42 process slots
        stage = stage_factory(StageConfig(
            max_processes=60,
            num_processes_at_startup=0,
            new_process_probability=0))

        with pytest.raises(ValueError) as exc_info:
            stage.setup()

        assert str(exc_info.value) == (
            'Stage config allows 60 processes at the same time, '
            'but there are only 42 process slots.')


class TestProcessCreationHardLimit:
    """Tests for the hard process creation limit counting lingering processes."""

    @pytest.fixture
    def auto_cpu_script(self):
        # Automation script that moves every newly created process to a CPU
        return compile(
            "def scheduler(events):\n"
            "    return [\n"
            "        {'type': 'process', 'pid': event.pid}\n"
            "        for event in events if event.etype == 'PROC_NEW'\n"
            "    ]\n",
            'test_script.py',
            'exec'
        )

    @pytest.fixture
    def saturated_stage(self, scene_manager, monkeypatch, auto_cpu_script):
        # Random is forced to its minimum, so each running process terminates
        # gracefully after one second (graceful termination roll of 1 over 100)
        monkeypatch.setattr(Random, 'get_number', lambda self_random, min, max: min)

        stage_config = StageConfig(
            num_processes_at_startup=42,
            new_process_probability=1.0,
            io_probability=0,
            graceful_termination_probability=0.01)
        stage = Stage('Test Stage', stage_config, script=auto_cpu_script)
        stage.scene_manager = scene_manager
        stage.setup()

        # Spawn all 42 startup processes
        for time in range(50, 2101, 50):
            stage.update(time, [])

        # Processes 1 to 4 terminate gracefully and linger on their CPUs,
        # holding both a thread and their pages
        for time in range(2150, 3501, 50):
            stage.update(time, [])

        processes = [child for child in stage.process_manager.children
                     if isinstance(child, Process)]
        assert len(processes) == 42
        assert len([
            child for child in stage.process_manager.children
            if isinstance(child, Process) and child.state == ProcessState.ENDED
        ]) == 4
        stats = stage.process_manager.get_current_stats()
        assert stats['alive_process_count'] == 38
        return stage

    def test_process_creation_refused_when_lingering_processes_fill_the_grid(
            self, saturated_stage):
        stage = saturated_stage

        # Keep stepping: no new process may spawn while alive + lingering = 42
        for time in range(3551, 4251, 50):
            stage.update(time, [])

        stats = stage.process_manager.get_current_stats()
        assert stats['alive_process_count'] == 38

    def test_process_creation_resumes_when_a_lingering_process_is_cleared(
            self, saturated_stage):
        stage = saturated_stage

        corpse = next(child for child in stage.process_manager.children
                      if isinstance(child, Process) and child.state == ProcessState.ENDED)
        position = (corpse.view.x + corpse.view.width / 2,
                    corpse.view.y + corpse.view.height / 2)
        stage.update(3525, [PlayerInput(PlayerInputType.MOUSE_LEFT_CLICK, {'position': position})])

        for time in range(3551, 4251, 50):
            stage.update(time, [])

        stats = stage.process_manager.get_current_stats()
        assert stats['alive_process_count'] == 39
