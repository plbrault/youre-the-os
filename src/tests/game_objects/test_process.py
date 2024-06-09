import pytest

from constants import LAST_ALIVE_STARVATION_LEVEL, DEAD_STARVATION_LEVEL, MAX_PAGES_PER_PROCESS, ONE_SECOND
from engine.game_event import GameEvent
from engine.game_event_type import GameEventType
from engine.random import Random
from game_objects.process import Process
from stage_config import StageConfig

class TestProcess:
    @pytest.fixture
    def stage(self, stage, monkeypatch):
        """
        Overrides stage fixture defined in src/tests/conftest.py.
        """
        monkeypatch.setattr(stage.process_manager, 'terminate_process', lambda process, by_user: True)
        monkeypatch.setattr(stage.process_manager, 'del_process', lambda process: None)
        return stage

    @pytest.fixture
    def stage_custom_config(self, stage_custom_config, monkeypatch):
        """
        Overrides stage_custom_config fixture defined in src/tests/conftest.py.
        """
        def create_stage(stage_config):
            stage = stage_custom_config(stage_config)
            monkeypatch.setattr(stage.process_manager, 'terminate_process', lambda process, by_user: True)
            monkeypatch.setattr(stage.process_manager, 'del_process', lambda process: None)
            return stage
        return create_stage

    def test_initial_property_values(self, stage):
        process = Process(1, stage)

        assert process.pid == 1
        assert process.time_between_starvation_levels == 10000
        assert process.current_starvation_level_duration == 0
        assert process.cpu == None
        assert process.has_cpu == False
        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False
        assert process.starvation_level == 1
        assert process.display_blink_color == False
        assert process.current_state_duration == 0
        assert process.is_progressing_to_happiness == False
        assert process.is_in_motion == False

    def test_starvation_when_idle(self, stage):
        process = Process(1, stage)

        for i in range(0, LAST_ALIVE_STARVATION_LEVEL):
            process.update(i * process.time_between_starvation_levels, [])
            assert process.starvation_level == i + 1

    def test_max_starvation(self, stage):
        process = Process(1, stage)

        for i in range(0, LAST_ALIVE_STARVATION_LEVEL):
            process.update(i * process.time_between_starvation_levels, [])

        assert process.starvation_level == LAST_ALIVE_STARVATION_LEVEL

        process.update(DEAD_STARVATION_LEVEL * process.time_between_starvation_levels, [])

        assert process.starvation_level == DEAD_STARVATION_LEVEL
        assert process.has_ended == True

    def test_starvation_with_custom_time_between_starvation_levels(self, stage):
        default_value = Process(1, stage).time_between_starvation_levels

        process = Process(
            2,
            stage,
            time_between_starvation_levels=default_value / 2
        )

        for i in range(0, LAST_ALIVE_STARVATION_LEVEL):
            process.update(i * process.time_between_starvation_levels, [])
            assert process.starvation_level == i + 1

    def test_current_starvation_level_duration(self, stage):
        process = Process(1, stage)

        assert process.current_starvation_level_duration == 0
        process.update(process.time_between_starvation_levels / 2, [])
        assert process.current_starvation_level_duration == process.time_between_starvation_levels / 2
        process.update(process.time_between_starvation_levels, [])
        assert process.current_starvation_level_duration == 0

    def test_use_cpu_when_first_cpu_is_available(self, stage):
        process = Process(1, stage)

        assert process.cpu == None
        assert process.has_cpu == False
        for i in range(0, stage.config.num_cpus):
            assert stage.process_manager.cpu_list[i].process == None

        process.use_cpu()

        assert process.has_cpu == True
        assert process.cpu == stage.process_manager.cpu_list[0]
        assert stage.process_manager.cpu_list[0].process == process
        for i in range(1, stage.config.num_cpus):
            assert stage.process_manager.cpu_list[i].process == None

        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False

    def test_use_cpu_when_first_cpu_is_unavailable(self, stage):
        process = Process(1, stage)

        assert process.cpu == None
        assert process.has_cpu == False
        for i in range(0, stage.config.num_cpus):
            assert stage.process_manager.cpu_list[i].process == None

        stage.process_manager.cpu_list[0].process = Process(2, stage)
        process.use_cpu()

        assert process.has_cpu == True
        assert process.cpu == stage.process_manager.cpu_list[1]
        assert stage.process_manager.cpu_list[0].process.pid == 2
        assert stage.process_manager.cpu_list[1].process == process
        for i in range(2, stage.config.num_cpus):
            assert stage.process_manager.cpu_list[i].process == None

        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False

    def test_use_cpu_when_all_cpus_are_unavailable(self, stage):
        process = Process(1, stage)

        assert process.cpu == None
        assert process.has_cpu == False
        for i in range(0, stage.config.num_cpus):
            assert stage.process_manager.cpu_list[i].process == None

        for i in range(0, stage.config.num_cpus):
            stage.process_manager.cpu_list[i].process = Process(i + 2, stage)

        process.use_cpu()

        assert process.cpu == None
        assert process.has_cpu == False
        for i in range(0, stage.config.num_cpus):
            assert stage.process_manager.cpu_list[i].process.pid == i + 2

        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False

    def test_use_cpu_when_already_using_cpu(self, stage):
        process = Process(1, stage)

        process.use_cpu()
        process.use_cpu()

        assert process.cpu == stage.process_manager.cpu_list[0]
        assert process.has_cpu == True
        assert stage.process_manager.cpu_list[0].process == process
        for i in range(1, stage.config.num_cpus):
            assert stage.process_manager.cpu_list[i].process == None

        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False

    def test_yield_cpu(self, stage):
        process = Process(1, stage)

        for i in range(0, stage.config.num_cpus - 1):
            stage.process_manager.cpu_list[i].process = Process(i + 2, stage)

        process.use_cpu()

        process.yield_cpu()
        assert process.cpu == None
        assert process.has_cpu == False
        for i in range(0, stage.config.num_cpus - 1):
            assert stage.process_manager.cpu_list[i].process.pid == i + 2
        assert stage.process_manager.cpu_list[3].process == None

        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False

    def test_yield_cpu_when_already_idle(self, stage):
        process = Process(1, stage)

        process.yield_cpu()
        assert process.cpu == None
        assert process.has_cpu == False
        for i in range(0, stage.config.num_cpus):
            assert stage.process_manager.cpu_list[i].process == None

        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False

    def test_toggle(self, stage):
        process = Process(1, stage)

        process.toggle()
        assert process.cpu != None
        assert process.has_cpu == True

        process.toggle()
        assert process.cpu == None
        assert process.has_cpu == False

    def test_unstarvation(self, stage):
        process = Process(1, stage)

        current_time = 0

        for i in range(1, LAST_ALIVE_STARVATION_LEVEL):
            current_time += process.time_between_starvation_levels
            process.update(current_time, [])

        process.use_cpu()
        assert process.starvation_level == LAST_ALIVE_STARVATION_LEVEL

        current_time += process.cpu.time_for_process_happiness
        process.update(current_time, [])
        assert process.starvation_level == 0

    def test_graceful_termination(self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            num_ram_rows=8,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0.01
        ))

        # Cause the random number generator to always provoke graceful termination
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process = Process(1, stage)
        process.use_cpu()

        process.update(1000, [])

        assert process.has_ended == True
        assert process.starvation_level == 0

    def test_use_cpu_min_page_creation(self, stage, monkeypatch):
        # Make sure that the minimum number of pages will be created
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process = Process(1, stage)

        with pytest.raises(KeyError):
            stage.page_manager.get_page(1, 0)

        process.use_cpu()

        assert stage.page_manager.get_page(1, 0).pid == 1
        for i in range(1, MAX_PAGES_PER_PROCESS):
            with pytest.raises(KeyError):
                stage.page_manager.get_page(1, i)

    def test_use_cpu_max_page_creation(self, stage, monkeypatch):
        # Make sure that the maximum number of pages will be created
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, stage)

        with pytest.raises(KeyError):
            stage.page_manager.get_page(1, 0)

        process.use_cpu()

        for i in range(1, MAX_PAGES_PER_PROCESS):
            assert stage.page_manager.get_page(1, i).pid == 1
        with pytest.raises(KeyError):
            stage.page_manager.get_page(1, 4)

    def test_new_page_creation_while_running(self, stage, monkeypatch):
        process = Process(1, stage)

        # Should cause the creation of a single page when the process starts running,
        # and then the creation a new page when the process is updated
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process.use_cpu()

        assert stage.page_manager.get_page(1, 0).pid == 1
        with pytest.raises(KeyError):
            stage.page_manager.get_page(1, 1)

        process.update(1000, [])

        assert stage.page_manager.get_page(1, 0).pid == 1
        assert stage.page_manager.get_page(1, 1).pid == 1

        # Should prevent the creation of a new page when the process is updated again
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process.update(2000, [])

        assert stage.page_manager.get_page(1, 0).pid == 1
        assert stage.page_manager.get_page(1, 1).pid == 1
        with pytest.raises(KeyError):
            stage.page_manager.get_page(1, 2)

    def test_use_cpu_when_already_has_pages(self, stage, monkeypatch):
        process = Process(1, stage)

        # Should cause the creation of a single page when the process is run for the first time
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)
        process.use_cpu()

        process.yield_cpu()

        # Should prevent the creation of new pages when the process is run again
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)
        process.use_cpu()

        assert stage.page_manager.get_page(1, 0).pid == 1
        for i in range(1, MAX_PAGES_PER_PROCESS):
            with pytest.raises(KeyError):
                stage.page_manager.get_page(1, i)

    def test_use_cpu_sets_pages_to_in_use(self, stage, monkeypatch):
        # Should cause the creation of the maximum number of pages when the process is run
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, stage)

        process.use_cpu()
        for i in range(0, MAX_PAGES_PER_PROCESS):
            assert stage.page_manager.get_page(1, i).in_use == True

        process.yield_cpu()
        process.use_cpu()
        for i in range(0, MAX_PAGES_PER_PROCESS):
            assert stage.page_manager.get_page(1, i).in_use == True

    def test_yield_cpu_sets_pages_to_not_in_use(self, stage, monkeypatch):
        # Should cause the creation of the maximum number of pages when the process is run
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, stage)

        process.use_cpu()
        process.yield_cpu()

        for i in range(0, MAX_PAGES_PER_PROCESS):
            assert stage.page_manager.get_page(1, i).in_use == False

    def test_set_page_to_swap_while_running(self, stage, monkeypatch):
        # Should cause the creation of the maximum number of pages when the process is run
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, stage)

        process.use_cpu()

        stage.page_manager.get_page(1, 0).swap()
        assert stage.page_manager.get_page(1, 0).in_swap == True

        process.update(0, [])

        assert process.is_blocked == True
        assert process.is_waiting_for_page == True
        assert process.is_waiting_for_io == False

    def test_set_page_to_swap_before_running(self, stage, monkeypatch):
        # Should cause the creation of the maximum number of pages when the process is run
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, stage)

        process.use_cpu()
        process.yield_cpu()

        stage.page_manager.get_page(1, 0).swap()
        assert stage.page_manager.get_page(1, 0).in_swap == True

        process.use_cpu()

        process.update(0, [])

        assert process.is_blocked == True
        assert process.is_waiting_for_page == True
        assert process.is_waiting_for_io == False

    def test_remove_page_from_swap_while_running(self, stage, monkeypatch):
        # Should cause the creation of the maximum number of pages when the process is run
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, stage)

        process.use_cpu()

        stage.page_manager.get_page(1, 0).swap()
        process.update(0, [])
        assert process.is_blocked == True

        stage.page_manager.get_page(1, 0).swap()
        process.update(0, [])

        assert process.is_blocked == False
        assert process.is_waiting_for_page == False
        assert process.is_waiting_for_io == False

    def test_yield_cpu_while_waiting_for_page(self, stage, monkeypatch):
        # Should cause the creation of the maximum number of pages when the process is run
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, stage)

        process.use_cpu()

        stage.page_manager.get_page(1, 0).swap()
        process.update(0, [])
        assert process.is_waiting_for_page == True

        process.yield_cpu()
        process.update(0, [])

        assert process.is_blocked == False
        assert process.is_waiting_for_page == False
        assert process.is_waiting_for_io == False

    def test_starvation_while_waiting_for_page(self, stage, monkeypatch):
        # Should cause the creation of the maximum number of pages when the process is run
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, stage)

        process.use_cpu()

        stage.page_manager.get_page(1, 0).swap()
        process.update(0, [])
        assert process.is_waiting_for_page == True

        for i in range(1, LAST_ALIVE_STARVATION_LEVEL):
            process.update(i * process.time_between_starvation_levels, [])
            assert process.starvation_level == i + 1

        process.update(LAST_ALIVE_STARVATION_LEVEL * process.time_between_starvation_levels, [])
        assert process.starvation_level == DEAD_STARVATION_LEVEL
        assert process.has_ended == True

    def test_page_deletion_when_process_is_killed(self, stage, monkeypatch):
        # Should cause the creation of the maximum number of pages when the process is run
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, stage)

        process.use_cpu()
        stage.page_manager.get_page(1, 0).swap()

        for i in range(1, DEAD_STARVATION_LEVEL):
            process.update(i * process.time_between_starvation_levels, [])
        assert process.has_ended == True

        with pytest.raises(KeyError):
            for i in range(1, 5):
                stage.page_manager.get_page(1, i)

    def test_page_deletion_when_process_is_gracefully_terminated(self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            num_ram_rows=8,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0.01
        ))

        # Should prevent graceful termination
        # Should also cause the creation of the maximum number of pages when the process is run
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, stage)
        process.use_cpu()
        process.update(1000, [])
        assert process.has_ended == False
        assert stage.page_manager.get_page(1, 0).pid == 1

        # Should cause graceful termination
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process.update(2000, [])

        assert process.has_ended == True
        assert process.starvation_level == 0

        with pytest.raises(KeyError):
            for i in range(0, 5):
                stage.page_manager.get_page(1, i)

    def test_process_blocks_for_io_event(self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            num_ram_rows=8,
            new_process_probability=0,
            io_probability=0.1,
            graceful_termination_probability=0
        ))

        # Cause the random number generator to always provoke an I/O event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process = Process(1, stage)

        process.use_cpu()
        process.update(0, [])
        assert process.is_waiting_for_io == False

        process.update(ONE_SECOND, [])

        assert process.is_blocked == True
        assert process.is_waiting_for_io == True
        assert process.is_waiting_for_page == False

    def test_process_continues_when_no_io_event(self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            num_ram_rows=8,
            new_process_probability=0,
            io_probability=0.1,
            graceful_termination_probability=0
        ))

        # Cause the random number generator to never provoke an I/O event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, stage)

        process.use_cpu()
        process.update(0, [])
        assert process.is_waiting_for_io == False

        process.update(1000, [])

        assert process.is_blocked == False
        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False

    def test_starvation_while_waiting_for_io_event(self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            num_ram_rows=8,
            new_process_probability=0,
            io_probability=0.1,
            graceful_termination_probability=0
        ))

        # Cause the random number generator to always provoke an I/O event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process = Process(1, stage)

        process.use_cpu()
        process.update(1000, [])
        assert process.is_waiting_for_io == True

        for i in range(1, LAST_ALIVE_STARVATION_LEVEL):
            process.update(i * process.time_between_starvation_levels, [])
            assert process.starvation_level == i + 1

        process.update(LAST_ALIVE_STARVATION_LEVEL * process.time_between_starvation_levels, [])
        assert process.starvation_level == DEAD_STARVATION_LEVEL
        assert process.has_ended == True
        assert process.is_blocked == False
        assert process.is_waiting_for_io == False

    def test_process_unblocks_when_io_event_is_processed(self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            num_ram_rows=8,
            new_process_probability=0,
            io_probability=0.1,
            graceful_termination_probability=0
        ))

        # Cause the random number generator to always provoke an I/O event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process = Process(1, stage)

        process.use_cpu()
        process.update(1000, [])
        assert process.is_waiting_for_io == True

        stage.process_manager.io_queue.update(1000, [])
        stage.process_manager.io_queue.process_events()

        assert process.is_blocked == False
        assert process.is_waiting_for_io == False

    def test_no_io_event_at_last_alive_starvation_level(self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            num_ram_rows=8,
            new_process_probability=0,
            io_probability=0.1,
            graceful_termination_probability=0
        ))

        process1 = Process(1, stage)
        process2 = Process(2, stage)

        current_time = 0
        for i in range(1, LAST_ALIVE_STARVATION_LEVEL):
            current_time += process1.time_between_starvation_levels
            process1.update(current_time, [])

        # Cause the random number generator to always provoke an I/O event
        # (excepted in tested case)
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process1.use_cpu()
        process2.use_cpu()

        assert process1.starvation_level == LAST_ALIVE_STARVATION_LEVEL
        assert process2.starvation_level == 1
        assert process1.is_waiting_for_io == False
        assert process2.is_waiting_for_io == False

        current_time += 1000
        process1.update(current_time, [])
        process2.update(current_time, [])

        assert process1.starvation_level == LAST_ALIVE_STARVATION_LEVEL
        assert process1.is_waiting_for_io == False
        assert process2.is_waiting_for_io == True

    def test_io_cooldown(self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            num_ram_rows=8,
            new_process_probability=0,
            io_probability=0.1,
            graceful_termination_probability=0
        ))

        process1 = Process(1, stage)
        process2 = Process(2, stage)

        # Cause the random number generator to always provoke an I/O event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process1.use_cpu()
        process1.update(1000, [])
        assert process1.is_waiting_for_io == True

        # Cause the random number generator to never provoke an I/O event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process2.use_cpu()
        process2.update(1000, [])
        assert process2.is_waiting_for_io == False

        # Cause the random number generator to always provoke an I/O event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        stage.process_manager.io_queue.update(1000, [])
        stage.process_manager.io_queue.process_events()
        assert process1.is_waiting_for_io == False

        process1.update(2000, [])
        process2.update(2000, [])
        assert process1.is_waiting_for_io == False
        assert process2.is_waiting_for_io == True

    def test_io_cooldown_deactivation(self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            num_ram_rows=8,
            new_process_probability=0,
            io_probability=0.1,
            graceful_termination_probability=0
        ))

        process = Process(1, stage)

        # Cause the random number generator to always provoke an I/O event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process.use_cpu()
        process.update(1000, [])
        assert process.is_waiting_for_io == True

        stage.process_manager.io_queue.update(1000, [])
        stage.process_manager.io_queue.process_events()
        assert process.is_waiting_for_io == False

        process.yield_cpu()
        process.use_cpu()
        process.update(2000, [])
        assert process.is_waiting_for_io == True

    def test_movement_animation(self, stage):
        process = Process(1, stage)

        target_x = 500
        target_y = 1000

        process.view.x = 0
        process.view.y = 0
        process.view.target_x = target_x
        process.view.target_y = target_y

        assert process.is_in_motion

        counter = 0
        while process.view.target_x != None or process.view.target_y != None:
            counter += 1
            process.update(counter, [])
            assert counter < 100 # prevents infinite loop if test fails

        assert process.view.x == target_x
        assert process.view.y == target_y
        assert not process.is_in_motion

    def test_click_when_idle(self, stage):
        process = Process(1, stage)
        process.view.set_xy(1000, 500)

        mouse_click_event = GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': (process.view.x, process.view.y) })
        process.update(1000, [mouse_click_event])

        assert process.has_cpu == True
        assert process.view.target_x == stage.process_manager.cpu_list[0].view.x
        assert process.view.target_y == stage.process_manager.cpu_list[0].view.y

    def test_click_during_moving_animation(self, stage):
        process = Process(1, stage)
        process.view.set_xy(1000, 500)
        process.use_cpu()

        assert process.has_cpu == True
        assert process.view.y != process.view.target_y

        mouse_click_event = GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': (process.view.x, process.view.y) })
        process.update(1000, [mouse_click_event])
        assert process.has_cpu == True

    def test_click_when_running(self, stage):
        process = Process(1, stage)
        stage.process_manager.cpu_list[0].process = Process(2, stage) # to force process to use a CPU with a different x position than itself
        process.use_cpu()

        assert process.has_cpu == True

        process.view.x = process.view.target_x
        process.view.y = process.view.target_y
        process.view.target_x = None
        process.view.target_y = None

        mouse_click_event = GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': (process.view.x, process.view.y) })
        process.update(1000, [mouse_click_event])

        assert process.has_cpu == False
        assert process.view.target_x == stage.process_manager.process_slots[0].view.x
        assert process.view.target_y == stage.process_manager.process_slots[0].view.y

    def test_click_when_gracefully_terminated(self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            num_ram_rows=8,
            new_process_probability=0,
            io_probability=0,
            graceful_termination_probability=0.01
        ))
        # Cause the random number generator to always provoke graceful termination
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process = Process(1, stage)
        process.use_cpu()
        process.update(1000, [])
        process.view.x = process.view.target_x
        process.view.y = process.view.target_y
        process.view.target_x = process.view.target_y = None

        assert process.has_ended == True

        mouse_click_event = GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': (process.view.x, process.view.y) })
        process.update(2000, [mouse_click_event])

        assert process.view.target_y <= -process.view.height

    def test_blinking_animation(self, stage):
        process = Process(1, stage)

        process.use_cpu()
        stage.page_manager.get_page(1, 0).swap()

        previous_blink_value = process.display_blink_color
        for i in range(1, 5):
            process.update(i * 200, [])
            assert process.display_blink_color != previous_blink_value
            previous_blink_value = process.display_blink_color

    def test_blinking_animation_deactivation(self, stage):
        process = Process(1, stage)

        process.use_cpu()
        stage.page_manager.get_page(1, 0).swap()
        process.update(1000, [])

        stage.page_manager.get_page(1, 0).swap()
        process.update(2000, [])

        for i in range(1, 5):
            process.update(i * 200, [])
            assert process.display_blink_color == False

    def test_sort_key(self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            num_ram_rows=8,
            new_process_probability=0,
            io_probability=0.1,
            graceful_termination_probability=0
        ))

        process_lowest_starvation = Process(1, stage)
        process_medium_starvation_1 = Process(3, stage)
        process_medium_starvation_2 = Process(4, stage)
        process_medium_starvation_plus_one_second = Process(5, stage)
        process_highest_starvation = Process(2, stage)
        process_blocked = Process(6, stage)

        # Cause the random number generator to never provoke an I/O event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        time = 0

        for i in range(2):
            time += process_highest_starvation.time_between_starvation_levels
            process_highest_starvation.update(time, [])
            process_medium_starvation_1.update(time, [])
            process_medium_starvation_2.update(time, [])
            process_medium_starvation_plus_one_second.update(time, [])
            process_blocked.update(time, [])

        process_lowest_starvation.use_cpu()
        process_lowest_starvation.update(time, [])
        process_lowest_starvation.yield_cpu()

        time += ONE_SECOND
        process_medium_starvation_plus_one_second.update(time, [])

        time += process_highest_starvation.time_between_starvation_levels - ONE_SECOND
        process_highest_starvation.update(time, [])
        process_blocked.update(time, [])

        time += ONE_SECOND
        # Cause the random number generator to always provoke an I/O event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)
        process_blocked.use_cpu()
        process_blocked.update(time, [])
        # Cause the random number generator to never provoke an I/O event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)
        process_blocked.yield_cpu()
        process_blocked.update(time, [])

        time += process_highest_starvation.time_between_starvation_levels - ONE_SECOND
        process_highest_starvation.update(time, [])

        assert process_lowest_starvation.starvation_level == 0
        assert process_medium_starvation_1.starvation_level == 3
        assert process_medium_starvation_2.starvation_level == 3
        assert process_medium_starvation_plus_one_second.starvation_level == 3
        assert process_highest_starvation.starvation_level == LAST_ALIVE_STARVATION_LEVEL
        assert process_blocked.starvation_level == LAST_ALIVE_STARVATION_LEVEL - 1

        assert not process_lowest_starvation.is_blocked
        assert not process_medium_starvation_1.is_blocked
        assert not process_medium_starvation_2.is_blocked
        assert not process_medium_starvation_plus_one_second.is_blocked
        assert not process_highest_starvation.is_blocked
        assert process_blocked.is_blocked

        assert not process_lowest_starvation.has_cpu
        assert not process_medium_starvation_1.has_cpu
        assert not process_medium_starvation_2.has_cpu
        assert not process_medium_starvation_plus_one_second.has_cpu
        assert not process_highest_starvation.has_cpu
        assert not process_blocked.has_cpu

        assert process_highest_starvation.sort_key < process_medium_starvation_plus_one_second.sort_key
        assert process_medium_starvation_plus_one_second.sort_key < process_medium_starvation_1.sort_key
        assert process_medium_starvation_1.sort_key == process_medium_starvation_2.sort_key
        assert process_medium_starvation_2.sort_key < process_lowest_starvation.sort_key
        assert process_lowest_starvation.sort_key < process_blocked.sort_key

    def test_sort_key_different_time_between_starvation_levels(self, stage_custom_config, monkeypatch):
        stage = stage_custom_config(StageConfig(
            num_cpus=4,
            num_processes_at_startup=14,
            num_ram_rows=8,
            new_process_probability=0,
            io_probability=0.1,
            graceful_termination_probability=0
        ))

        process_1 = Process(1, stage, time_between_starvation_levels=10000)
        process_2 = Process(2, stage, time_between_starvation_levels=10000)
        process_3 = Process(3, stage, time_between_starvation_levels=8000)

        process_1.update(5000, [])
        process_2.update(8000, [])
        process_3.update(7000, [])

        assert process_3.sort_key < process_2.sort_key
        assert process_2.sort_key < process_1.sort_key

        process_1.update(10000, [])
        process_2.update(10000, [])
        process_3.update(8000, [])

        process_1.update(18000, [])
        process_2.update(17000, [])
        process_3.update(15999, [])

        assert process_1.starvation_level == 2
        assert process_2.starvation_level == 2
        assert process_3.starvation_level == 2

        assert process_1.sort_key < process_2.sort_key
        assert process_3.sort_key < process_2.sort_key

        process_1.update(20000, [])
        process_2.update(20000, [])

        assert process_1.starvation_level == 3
        assert process_2.starvation_level == 3
        assert process_3.starvation_level == 2

        assert process_1.sort_key == process_2.sort_key
        assert process_1.sort_key < process_3.sort_key
