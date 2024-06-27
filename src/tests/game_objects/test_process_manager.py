import pytest

from constants import ONE_SECOND
from engine.game_manager import GameManager
from engine.random import Random
from game_objects.cpu import Cpu
from game_objects.io_queue import IoQueue
from game_objects.process_manager import ProcessManager
from game_objects.process_slot import ProcessSlot
from scenes.stage import Stage
from stage_config import StageConfig

class TestProcessManager:
    @pytest.fixture
    def stage_config(self):
        return StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            max_processes=42,
            new_process_probability=0.05,
            priority_process_probability=0,
        )

    @pytest.fixture
    def stage(self, stage_custom_config, stage_config):
        return stage_custom_config(stage_config)

    def test_setup(self, stage):
        process_manager = ProcessManager(stage)
        process_manager.setup()

        assert process_manager.stage == stage

        assert len(process_manager.cpu_list) == stage.config.num_cpus
        for cpu in process_manager.cpu_list:
            assert isinstance(cpu, Cpu)

        assert len(process_manager.process_slots) == stage.config.max_processes
        for process_slot in process_manager.process_slots:
            assert isinstance(process_slot, ProcessSlot)

        assert isinstance(process_manager.io_queue, IoQueue)

        assert process_manager.user_terminated_process_count == 0

    def test_initial_process_creation(self, stage):
        process_manager = ProcessManager(stage)
        process_manager.setup()

        time = 0.0
        process_count = 0
        iteration_count = 0

        while process_count < stage.config.num_processes_at_startup and iteration_count < 1000:
            iteration_count += 1
            process_manager.update(int(time), [])
            time += ONE_SECOND / GameManager.fps

            process_count = len([
                process_slot for process_slot in process_manager.process_slots if process_slot.process is not None
            ])

        assert process_count == stage.config.num_processes_at_startup

    @pytest.fixture
    def ready_process_manager(self, stage, monkeypatch):
        # Cause the random number generator to never provoke creation of new process
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process_manager = ProcessManager(stage)
        process_manager.setup()

        monkeypatch.setattr(Stage, 'process_manager', property(lambda self: process_manager))

        time = 0.0
        process_count = 0
        iteration_count = 0

        while process_count < stage.config.num_processes_at_startup and iteration_count < 100:
            iteration_count += 1
            process_manager.update(int(time), [])
            time += ONE_SECOND / GameManager.fps

            process_count = len([
                process_slot for process_slot in process_manager.process_slots if process_slot.process is not None
            ])

        # Bring back normal number generator
        monkeypatch.setattr(Random, 'get_number', Random.get_number)

        return process_manager

    def test_get_process(self, ready_process_manager, stage_config):
        process_manager = ready_process_manager

        for i in range(1, stage_config.num_processes_at_startup + 1):
            assert process_manager.get_process(i).pid == i

    def test_del_process(self, ready_process_manager):
        process_manager = ready_process_manager

        process = process_manager.get_process(1)
        process_manager.del_process(process)

        with pytest.raises(KeyError):
            process_manager.get_process(1)

    def test_terminate_idle_process_by_user(self, ready_process_manager):
        process_manager = ready_process_manager

        process = process_manager.get_process(1)

        process_slot = next(
            process_slot for process_slot
                in process_manager.process_slots if process_slot.process == process
        )

        process_manager.terminate_process(process, True)

        assert process_manager.user_terminated_process_count == 1
        assert process_slot.process is None

        # Validate that the process is now in a terminated process slot
        new_process_slot = next(
            child for child in process_manager.children
                if isinstance(child, ProcessSlot) and child.process == process
        )
        assert new_process_slot not in process_manager.process_slots

    def test_terminate_active_process_by_user(self, ready_process_manager):
        process_manager = ready_process_manager

        process = process_manager.get_process(1)

        process.use_cpu()
        cpu = next(cpu for cpu in process_manager.cpu_list if cpu.process == process)

        process_manager.terminate_process(process, True)

        assert process_manager.user_terminated_process_count == 1
        assert cpu.process is None

        # Validate that the process is NOT in a terminated process slot
        new_process_slot = next(
            child for child in process_manager.children
                if isinstance(child, ProcessSlot) and child.process == process
        )
        assert new_process_slot not in process_manager.process_slots

    def test_terminate_active_process_not_by_user(self, ready_process_manager):
        process_manager = ready_process_manager

        process = process_manager.get_process(1)

        process.use_cpu()
        cpu = next(cpu for cpu in process_manager.cpu_list if cpu.process == process)

        process_manager.terminate_process(process, False)

        assert process_manager.user_terminated_process_count == 0
        assert cpu.process == process

    def test_create_new_process_at_random(self, ready_process_manager, stage_config, monkeypatch):
        process_manager = ready_process_manager

        # Cause the random number generator to never provoke creation of new process
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process_manager.update(5000, [])
        assert len([
                process_slot for process_slot in process_manager.process_slots if process_slot.process is not None
            ]) == stage_config.num_processes_at_startup

        # Cause the random number generator to always provoke creation of new process
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process_manager.update(6000, [])

        assert len([
                process_slot for process_slot in process_manager.process_slots if process_slot.process is not None
            ]) == stage_config.num_processes_at_startup + 1

    def test_create_new_process_at_interval(self, ready_process_manager, stage_config, monkeypatch):
        process_manager = ready_process_manager

        # Cause the random number generator to never provoke creation of new process
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        interval = int(1 / stage_config.new_process_probability * 1000)
        assert interval > 5000

        process_manager.update(5000, [])
        assert len([
                process_slot for process_slot in process_manager.process_slots if process_slot.process is not None
            ]) == stage_config.num_processes_at_startup

        process_manager.update(interval + 5000, [])
        assert len([
                process_slot for process_slot in process_manager.process_slots if process_slot.process is not None
            ]) == stage_config.num_processes_at_startup + 1

        process_manager.update(interval + 6000, [])
        assert len([
                process_slot for process_slot in process_manager.process_slots if process_slot.process is not None
            ]) == stage_config.num_processes_at_startup + 1

        process_manager.update(interval * 2 + 5000, [])
        assert len([
                process_slot for process_slot in process_manager.process_slots if process_slot.process is not None
            ]) == stage_config.num_processes_at_startup + 2
            