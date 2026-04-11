import pytest

from constants import DEAD_STARVATION_LEVEL, ONE_SECOND, FRAMERATE
from engine.game_manager import GameManager
from engine.random import Random
from config.cpu_config import CpuConfig
from config.stage_config import StageConfig
from scene_objects.process import Process
from scenes.stage import Stage


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

    def test_game_over_initially_false(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=4,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
        ))

        assert not stage.game_over

    def test_game_over_setter(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=4,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
        ))

        assert not stage.game_over
        stage.game_over = True
        assert stage.game_over

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

    def test_is_paused_initially_false(self, stage_custom_config):
        stage = stage_custom_config(StageConfig(
            cpu_config=CpuConfig(num_cores=4),
            num_processes_at_startup=4,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
        ))

        assert not stage.is_paused

    def test_game_over(self, stage_custom_config):
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

        assert not stage.game_over

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

        assert stage.game_over

    def test_game_over_does_not_trigger_before_max_terminated(self, stage_custom_config):
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

        assert not stage.game_over

    def test_game_over_does_not_trigger_while_processes_in_motion(self, stage_custom_config):
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
            assert not stage.game_over