import pytest

from constants import LAST_ALIVE_STARVATION_LEVEL, DEAD_STARVATION_LEVEL, FRAMERATE, ONE_SECOND, ONE_MINUTE
from engine.game_manager import GameManager
from engine.random import Random
from game_objects.checkbox import Checkbox
from game_objects.cpu import Cpu
from game_objects.io_queue import IoQueue
from game_objects.process import Process
from game_objects.process_manager import ProcessManager
from game_objects.process_slot import ProcessSlot
from game_objects.sort_button import SortButton
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
        process_manager = stage.process_manager
        stage.setup()

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

        process_manager = stage.process_manager
        stage.setup

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

    @pytest.fixture
    def ready_process_manager_custom_config(self, stage_custom_config, monkeypatch):
        def create_process_manager(stage_config):
            # Cause the random number generator to never provoke creation of new process
            monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

            stage = stage_custom_config(stage_config)
            stage.setup()
            process_manager = stage.process_manager

            time = 0.0
            process_count = 0
            iteration_count = 0

            while (
                process_count < stage.config.num_processes_at_startup
                and iteration_count < 100
            ):
                iteration_count += 1
                process_manager.update(int(time), [])
                time += ONE_SECOND / GameManager.fps

                used_process_slots = [
                    process_slot for process_slot in process_manager.process_slots if process_slot.process is not None
                ]
                process_count = len(used_process_slots)

            # Bring back normal number generator
            monkeypatch.setattr(Random, 'get_number', Random.get_number)

            return process_manager
        return create_process_manager

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

    def test_update_removes_process_out_of_screen(self, ready_process_manager_custom_config):
        process_manager = ready_process_manager_custom_config(StageConfig(
            num_processes_at_startup = 1,
            new_process_probability = 0,
            graceful_termination_probability = 1,
            io_probability = 0
        ))

        process = process_manager.get_process(1)
        process.use_cpu()

        process_is_in_children = False
        for child in process_manager.children:
            if child == process:
                process_is_in_children = True
                break
        assert process_is_in_children

        time = 2000

        process_manager.update(time, [])
        assert process.has_ended

        process.yield_cpu()

        counter = 0
        while process.view.y > -process.view.height and counter < 100000:
            process_is_in_children = False
            for child in process_manager.children:
                if isinstance(child, Process) and child.pid == 1:
                    process_is_in_children = True
                    break
            assert process_is_in_children
            counter += 1
            time += ONE_SECOND / FRAMERATE
            process_manager.update(int(time), [])
        assert counter < 100000

        process_is_in_children = False
        for child in process_manager.children:
            if isinstance(child, Process) and child.pid == 1:
                process_is_in_children = True
                break
        assert not process_is_in_children

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

    def test_show_sort_button(self, ready_process_manager_custom_config):
        stage_config = StageConfig(
            num_processes_at_startup = 0,
            new_process_probability = 0,
            time_ms_to_show_sort_button = 6 * ONE_MINUTE
        )
        process_manager = ready_process_manager_custom_config(stage_config)

        sort_button = None
        for child in process_manager.children:
            if isinstance(child, SortButton):
                sort_button = child
                break

        assert sort_button is not None
        assert not sort_button.visible

        for i in range(int(stage_config.time_ms_to_show_sort_button / ONE_SECOND)):
            process_manager.stage.update(i * ONE_SECOND, [])
            assert not sort_button.visible

        process_manager.stage.update(stage_config.time_ms_to_show_sort_button, [])
        process_manager.stage.update(stage_config.time_ms_to_show_sort_button + 1, [])
        # We execute one extra update because the process manager determines the visibility of the button
        # based on the stage's UptimeManager, which may get updated after the ProcessManager.
        assert sort_button.visible

    def test_show_auto_sort_checkbox(self, ready_process_manager_custom_config):
        stage_config = StageConfig(
            num_processes_at_startup = 0,
            new_process_probability = 0,
            time_ms_to_show_auto_sort_checkbox = 12 * ONE_MINUTE
        )
        process_manager = ready_process_manager_custom_config(stage_config)

        auto_sort_checkbox = None
        for child in process_manager.children:
            if isinstance(child, Checkbox) and child.text == 'Auto-Sort':
                auto_sort_checkbox = child
                break

        assert auto_sort_checkbox is not None
        assert not auto_sort_checkbox.visible

        for i in range(int(stage_config.time_ms_to_show_auto_sort_checkbox / ONE_SECOND)):
            process_manager.stage.update(i * ONE_SECOND, [])
            assert not auto_sort_checkbox.visible

        process_manager.stage.update(stage_config.time_ms_to_show_auto_sort_checkbox, [])
        process_manager.stage.update(stage_config.time_ms_to_show_auto_sort_checkbox + 1, [])
        # We execute one extra update because the process manager determines the visibility of the checkbox
        # based on the stage's UptimeManager, which may get updated after the ProcessManager.
        assert auto_sort_checkbox.visible

    def test_get_current_stats(self, ready_process_manager_custom_config):
        process_manager_1 = ready_process_manager_custom_config(StageConfig(
            num_processes_at_startup = 10,
            new_process_probability = 0,
            graceful_termination_probability = 0,
            io_probability = 0
        ))

        stats = process_manager_1.get_current_stats()
        assert stats['alive_process_count'] == 10
        assert stats['alive_process_count_by_starvation_level'][0] == 0
        assert stats['alive_process_count_by_starvation_level'][1] == 10
        for i in range(2, DEAD_STARVATION_LEVEL):
            assert stats['alive_process_count_by_starvation_level'][i] == 0
        assert stats['blocked_active_process_count'] == 0
        assert stats['io_event_count'] == 0
        assert stats['gracefully_terminated_process_count'] == 0
        assert stats['user_terminated_process_count'] == 0

        time = 0
        process1 = process_manager_1.get_process(1)
        while process1.starvation_level < DEAD_STARVATION_LEVEL and time < 1000000:
            process1.update(time, [])
            time += ONE_SECOND

        time = 0
        process2 = process_manager_1.get_process(2)
        while process2.starvation_level < DEAD_STARVATION_LEVEL - 1 and time < 1000000:
            process2.update(time, [])
            time += ONE_SECOND

        stats = process_manager_1.get_current_stats()
        assert stats['alive_process_count'] == 9
        assert stats['alive_process_count_by_starvation_level'][0] == 0
        assert stats['alive_process_count_by_starvation_level'][1] == 8
        assert stats['alive_process_count_by_starvation_level'][LAST_ALIVE_STARVATION_LEVEL] == 1
        for i in range(2, LAST_ALIVE_STARVATION_LEVEL):
            assert stats['alive_process_count_by_starvation_level'][i] == 0
        assert stats['blocked_active_process_count'] == 0
        assert stats['io_event_count'] == 0
        assert stats['gracefully_terminated_process_count'] == 0
        assert stats['user_terminated_process_count'] == 1

        process_manager_2 = ready_process_manager_custom_config(StageConfig(
            num_processes_at_startup = 10,
            new_process_probability = 1,
            graceful_termination_probability = 0,
            io_probability = 0
        ))

        stats = process_manager_2.get_current_stats()
        assert stats['alive_process_count'] == 10

        process_manager_2.update(2000, [])

        stats = process_manager_2.get_current_stats()
        assert stats['alive_process_count'] == 11

        process_manager_3 = ready_process_manager_custom_config(StageConfig(
            num_processes_at_startup = 10,
            new_process_probability = 0,
            graceful_termination_probability = 1,
            io_probability = 0
        ))

        stats = process_manager_3.get_current_stats()
        assert stats['alive_process_count'] == 10

        process = process_manager_3.get_process(1)
        process.use_cpu()
        process.update(2000, [])

        stats = process_manager_3.get_current_stats()
        assert stats['alive_process_count'] == 9
        assert stats['gracefully_terminated_process_count'] == 1
        assert stats['user_terminated_process_count'] == 0
        assert stats['alive_process_count_by_starvation_level'][0] == 0
        assert stats['alive_process_count_by_starvation_level'][1] == 9
        for i in range(2, DEAD_STARVATION_LEVEL):
            assert stats['alive_process_count_by_starvation_level'][i] == 0

        process_manager_4 = ready_process_manager_custom_config(StageConfig(
            num_processes_at_startup = 10,
            new_process_probability = 0,
            graceful_termination_probability = 0,
            io_probability = 1
        ))

        stats = process_manager_4.get_current_stats()
        assert stats['blocked_active_process_count'] == 0

        process = process_manager_4.get_process(1)
        process.use_cpu()
        process.update(2000, [])

        stats = process_manager_4.get_current_stats()
        assert stats['blocked_active_process_count'] == 1

    def test_sort(self, ready_process_manager_custom_config):
        process_manager = ready_process_manager_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=5,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0,
            time_ms_to_show_sort_button=0,
        ))

        process_1 = process_manager.get_process(1)
        process_2 = process_manager.get_process(2)
        process_3 = process_manager.get_process(3)
        process_4 = process_manager.get_process(4)

        print('PROCESS 1 IN MOTION', process_1.is_in_motion)
        print('PROCESS 2 IN MOTION', process_2.is_in_motion)
        print('PROCESS 3 IN MOTION', process_3.is_in_motion)
        print('PROCESS 4 IN MOTION', process_4.is_in_motion)

        process_1.update(1000, [])
        process_2.update(2000, [])
        process_3.update(3000, [])
        process_4.update(4000, [])

        assert process_4.sort_key < process_3.sort_key < process_2.sort_key < process_1.sort_key
        assert process_manager.process_slots[0].process == process_1
        assert process_manager.process_slots[1].process == process_2
        assert process_manager.process_slots[2].process == process_3
        assert process_manager.process_slots[3].process == process_4

        process_manager.get_process(5).use_cpu()
        active_process = process_manager.get_process(5)

        sort_button = None
        for child in process_manager.children:
            if isinstance(child, SortButton):
                sort_button = child
                break

        assert sort_button.visible
        assert not sort_button.disabled

        process_manager.sort_idle_processes()

        process_manager.update(4000, [])
        assert sort_button.disabled

        time = 4000
        while sort_button.disabled and time < 10000:
            time += ONE_SECOND / FRAMERATE
            process_manager.update(time, [])

        assert not sort_button.disabled
         