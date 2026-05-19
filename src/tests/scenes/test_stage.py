import pytest

from constants import DEAD_STARVATION_LEVEL, ONE_SECOND, FRAMERATE
from engine.game_manager import GameManager
from engine.modal import Modal
from engine.modal_view import ModalView
from engine.random import Random
from config.cpu_config import CpuConfig
from config.stage_config import StageConfig
from scene_objects.game_over_dialog import GameOverDialog
from scene_objects.process import Process
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
    def __init__(self, victory_time=None, defeat_time=None, **kwargs):
        super().__init__(**kwargs)
        self.victory_time = victory_time
        self.defeat_time = defeat_time
        self.on_start_call_count = 0
        self.on_victory_call_count = 0
        self.on_defeat_call_count = 0

    def check_victory(self, current_time):
        if self.victory_time is not None:
            return current_time > self.victory_time
        return False

    def check_defeat(self, current_time):
        if self.defeat_time is not None:
            return current_time > self.defeat_time
        return False

    def on_start(self):
        self.on_start_call_count += 1

    def on_victory(self):
        self.on_victory_call_count += 1

    def on_defeat(self):
        self.on_defeat_call_count += 1


class TestStageStateMachine:
    """Tests for the Stage state machine transitions and behavior per the design spec."""

    @pytest.fixture
    def mock_stage(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
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

    def test_starting_ignores_invalid_events(self, mock_stage):
        invalid_events = [
            StateEvent.VICTORY_DETECTED,
            StateEvent.DEFEAT_DETECTED,
            StateEvent.PROCESSES_SETTLED,
            StateEvent.DELAY_ELAPSED,
        ]
        for event in invalid_events:
            mock_stage.apply_state_transition(event)
            assert mock_stage.state == StageState.STARTING

    def test_playing_ignores_invalid_events(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        invalid_events = [
            StateEvent.START,
            StateEvent.PROCESSES_SETTLED,
            StateEvent.DELAY_ELAPSED,
        ]
        for event in invalid_events:
            mock_stage.apply_state_transition(event)
            assert mock_stage.state == StageState.PLAYING

    def test_awaiting_victory_ignores_invalid_events(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.VICTORY_DETECTED)
        invalid_events = [
            StateEvent.START,
            StateEvent.VICTORY_DETECTED,
            StateEvent.DEFEAT_DETECTED,
            StateEvent.DELAY_ELAPSED,
        ]
        for event in invalid_events:
            mock_stage.apply_state_transition(event)
            assert mock_stage.state == StageState.AWAITING_VICTORY

    def test_awaiting_defeat_ignores_invalid_events(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.DEFEAT_DETECTED)
        invalid_events = [
            StateEvent.START,
            StateEvent.VICTORY_DETECTED,
            StateEvent.DEFEAT_DETECTED,
            StateEvent.DELAY_ELAPSED,
        ]
        for event in invalid_events:
            mock_stage.apply_state_transition(event)
            assert mock_stage.state == StageState.AWAITING_DEFEAT

    def test_victory_ignores_invalid_events(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.VICTORY_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        invalid_events = [
            StateEvent.START,
            StateEvent.VICTORY_DETECTED,
            StateEvent.DEFEAT_DETECTED,
            StateEvent.PROCESSES_SETTLED,
        ]
        for event in invalid_events:
            mock_stage.apply_state_transition(event)
            assert mock_stage.state == StageState.VICTORY

    def test_defeat_ignores_invalid_events(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.DEFEAT_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        invalid_events = [
            StateEvent.START,
            StateEvent.VICTORY_DETECTED,
            StateEvent.DEFEAT_DETECTED,
            StateEvent.PROCESSES_SETTLED,
        ]
        for event in invalid_events:
            mock_stage.apply_state_transition(event)
            assert mock_stage.state == StageState.DEFEAT

    def test_ended_ignores_all_events(self, mock_stage):
        mock_stage.apply_state_transition(StateEvent.START)
        mock_stage.apply_state_transition(StateEvent.VICTORY_DETECTED)
        mock_stage.apply_state_transition(StateEvent.PROCESSES_SETTLED)
        mock_stage.apply_state_transition(StateEvent.DELAY_ELAPSED)
        assert mock_stage.state == StageState.ENDED
        all_events = [
            StateEvent.START,
            StateEvent.VICTORY_DETECTED,
            StateEvent.DEFEAT_DETECTED,
            StateEvent.PROCESSES_SETTLED,
            StateEvent.DELAY_ELAPSED,
        ]
        for event in all_events:
            mock_stage.apply_state_transition(event)
            assert mock_stage.state == StageState.ENDED


class TestStageUpdateBehavior:
    """Tests for the Stage update() method behavior by state."""

    @pytest.fixture
    def mock_stage(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
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
            config=StageConfig(num_processes_at_startup=0),
            victory_time=0,
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
            config=StageConfig(num_processes_at_startup=0),
            victory_time=500,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])

        stage.update(600, [])
        assert stage.state == StageState.AWAITING_VICTORY

    def test_playing_transitions_to_awaiting_defeat_on_defeat(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            defeat_time=500,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])

        stage.update(600, [])
        assert stage.state == StageState.AWAITING_DEFEAT

    def test_playing_victory_takes_precedence_over_defeat(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            victory_time=500,
            defeat_time=500,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])

        stage.update(600, [])
        assert stage.state == StageState.AWAITING_VICTORY

    def test_awaiting_victory_transitions_to_victory_when_processes_settle(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            victory_time=500,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(600, [])

        assert stage.state == StageState.AWAITING_VICTORY

        stage.update(601, [])
        assert stage.state == StageState.VICTORY

    def test_awaiting_defeat_transitions_to_defeat_when_processes_settle(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            defeat_time=500,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(600, [])

        assert stage.state == StageState.AWAITING_DEFEAT

        stage.update(601, [])
        assert stage.state == StageState.DEFEAT

    def test_victory_waits_one_second_before_on_victory(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            victory_time=500,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(600, [])
        stage.update(601, [])

        assert stage.state == StageState.VICTORY
        assert stage.on_victory_call_count == 0

        stage.update(601 + ONE_SECOND, [])
        assert stage.on_victory_call_count == 0

        stage.update(601 + ONE_SECOND + 1, [])
        assert stage.on_victory_call_count == 1
        assert stage.state == StageState.ENDED

    def test_defeat_waits_one_second_before_on_defeat(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            defeat_time=500,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(600, [])
        stage.update(601, [])

        assert stage.state == StageState.DEFEAT
        assert stage.on_defeat_call_count == 0

        stage.update(601 + ONE_SECOND, [])
        assert stage.on_defeat_call_count == 0

        stage.update(601 + ONE_SECOND + 1, [])
        assert stage.on_defeat_call_count == 1
        assert stage.state == StageState.ENDED

    def test_on_victory_called_only_once(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            victory_time=500,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(600, [])
        stage.update(601, [])
        stage.update(601 + ONE_SECOND + 1, [])

        assert stage.on_victory_call_count == 1

        stage.update(601 + ONE_SECOND + 2, [])
        stage.update(601 + ONE_SECOND + 3, [])
        assert stage.on_victory_call_count == 1

    def test_on_defeat_called_only_once(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            defeat_time=500,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(600, [])
        stage.update(601, [])
        stage.update(601 + ONE_SECOND + 1, [])

        assert stage.on_defeat_call_count == 1

        stage.update(601 + ONE_SECOND + 2, [])
        stage.update(601 + ONE_SECOND + 3, [])
        assert stage.on_defeat_call_count == 1

    def test_ended_state_does_nothing_on_update(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            victory_time=500,
        )
        stage.scene_manager = scene_manager
        stage.setup()
        stage.update(0, [])
        stage.update(600, [])
        stage.update(601, [])
        stage.update(601 + ONE_SECOND + 1, [])

        assert stage.state == StageState.ENDED
        assert stage.on_victory_call_count == 1

        stage.update(10000, [])
        assert stage.state == StageState.ENDED
        assert stage.on_victory_call_count == 1

    def test_stage_not_completed_when_neither_condition_met(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
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


class TestStageCompletedProperty:
    """Tests for the stage_completed property based on the state machine."""

    @pytest.fixture
    def mock_stage(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
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
        stage = Stage('Test', StageConfig(num_processes_at_startup=0))
        stage.scene_manager = scene_manager
        stage.setup()
        stage.on_start()

    def test_on_victory_default_is_no_op(self, scene_manager):
        stage = Stage('Test', StageConfig(num_processes_at_startup=0))
        stage.scene_manager = scene_manager
        stage.setup()

        assert stage.modal is None
        stage.on_victory()
        assert stage.modal is None

    def test_on_defeat_default_shows_game_over_dialog(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=4,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
        ))

        assert stage.modal is None
        stage.on_defeat()
        assert isinstance(stage.modal, GameOverDialog)

    def test_reset_resets_state_to_starting(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            victory_time=500,
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(0, [])
        stage.update(600, [])
        assert stage.state == StageState.AWAITING_VICTORY

        stage.reset()
        assert stage.state == StageState.STARTING

    def test_reset_allows_on_start_to_fire_again(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            victory_time=500,
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
            config=StageConfig(num_processes_at_startup=0),
            victory_time=500,
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(0, [])
        stage.update(600, [])
        stage.update(601, [])
        stage.update(601 + ONE_SECOND + 1, [])
        assert stage.on_victory_call_count == 1

        stage.reset()

        stage.update(0, [])
        stage.update(600, [])
        stage.update(601, [])
        stage.update(601 + ONE_SECOND + 1, [])
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

        stage.show_modal(StubModal())

        stage.reset()

        assert stage.modal is None

    def test_reset_routes_events_to_scene_objects(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=4,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
        ))

        stage.show_modal(StubModal())
        stage.reset()

        update_received = False
        original_update = stage.process_manager.update

        def spy_update(current_time, events):
            nonlocal update_received
            update_received = True
            original_update(current_time, events)

        stage.process_manager.update = spy_update
        stage.update(0, [])

        assert update_received

    def test_stage_completed_via_victory(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            victory_time=500
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(400, [])
        assert not stage.stage_completed
        assert stage.on_victory_call_count == 0

        stage.update(600, [])
        assert not stage.stage_completed
        assert stage.on_victory_call_count == 0

        stage.update(601, [])
        assert stage.stage_completed
        assert stage.on_victory_call_count == 0

        stage.update(601 + ONE_SECOND, [])
        assert stage.on_victory_call_count == 0

        stage.update(601 + ONE_SECOND + 1, [])
        assert stage.on_victory_call_count == 1

        stage.update(601 + ONE_SECOND + 2, [])
        assert stage.on_victory_call_count == 1

    def test_stage_completed_via_defeat(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=0),
            defeat_time=500
        )
        stage.scene_manager = scene_manager
        stage.setup()

        stage.update(400, [])
        assert not stage.stage_completed
        assert stage.on_defeat_call_count == 0

        stage.update(600, [])
        assert not stage.stage_completed
        assert stage.on_defeat_call_count == 0

        stage.update(601, [])
        assert stage.stage_completed
        assert stage.on_defeat_call_count == 0

        stage.update(601 + ONE_SECOND, [])
        assert stage.on_defeat_call_count == 0

        stage.update(601 + ONE_SECOND + 1, [])
        assert stage.on_defeat_call_count == 1

        stage.update(601 + ONE_SECOND + 2, [])
        assert stage.on_defeat_call_count == 1

    def test_stage_completion_waits_for_processes_to_stop(self, scene_manager):
        stage = MockStage(
            name='Test',
            config=StageConfig(num_processes_at_startup=1),
            victory_time=500
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