import pytest
from lib.constants import LAST_ALIVE_STARVATION_LEVEL, DEAD_STARVATION_LEVEL, MAX_PAGES_PER_PROCESS
from lib.random import Random

from game_objects.process import Process

class TestProcess:
    @property
    def starvation_interval(self):
        return 10000

    @property
    def time_to_unstarve(self):
        return 5000

    def test_initial_property_values(self, game):
        process = Process(1, game)

        assert process.pid == 1
        assert process.has_cpu == False
        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False
        assert process.starvation_level == 1
        assert process.display_blink_color == False
        assert process.current_state_duration == 0
        assert process.is_progressing_to_happiness == False

    def test_starvation_when_idle(self, game):
        process = Process(1, game)

        for i in range(0, LAST_ALIVE_STARVATION_LEVEL):
            process.update(i * self.starvation_interval, [])
            assert process.starvation_level == i + 1

    def test_max_starvation(self, game, monkeypatch):
        monkeypatch.setattr(game.process_manager, 'terminate_process', lambda process, by_user: True)
        monkeypatch.setattr(game.process_manager, 'del_process', lambda process: None)

        process = Process(1, game)

        for i in range(0, LAST_ALIVE_STARVATION_LEVEL):
            process.update(i * self.starvation_interval, [])

        assert process.starvation_level == LAST_ALIVE_STARVATION_LEVEL

        process.update(DEAD_STARVATION_LEVEL * self.starvation_interval, [])

        assert process.starvation_level == DEAD_STARVATION_LEVEL
        assert process.has_ended == True

    def test_use_cpu_when_first_cpu_is_available(self, game):
        process = Process(1, game)

        assert process.has_cpu == False
        for i in range(0, game.config['num_cpus']):
            assert game.process_manager.cpu_list[i].process == None

        process.use_cpu()

        assert process.has_cpu == True
        assert game.process_manager.cpu_list[0].process == process
        for i in range(1, game.config['num_cpus']):
            assert game.process_manager.cpu_list[i].process == None

        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False

    def test_use_cpu_when_first_cpu_is_unavailable(self, game):
        process = Process(1, game)

        assert process.has_cpu == False
        for i in range(0, game.config['num_cpus']):
            assert game.process_manager.cpu_list[i].process == None

        game.process_manager.cpu_list[0].process = Process(2, game)
        process.use_cpu()

        assert process.has_cpu == True
        assert game.process_manager.cpu_list[0].process.pid == 2
        assert game.process_manager.cpu_list[1].process == process
        for i in range(2, game.config['num_cpus']):
            assert game.process_manager.cpu_list[i].process == None

        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False

    def test_use_cpu_when_all_cpus_are_unavailable(self, game):
        process = Process(1, game)

        assert process.has_cpu == False
        for i in range(0, game.config['num_cpus']):
            assert game.process_manager.cpu_list[i].process == None

        for i in range(0, game.config['num_cpus']):
            game.process_manager.cpu_list[i].process = Process(i + 2, game)

        process.use_cpu()

        assert process.has_cpu == False
        for i in range(0, game.config['num_cpus']):
            assert game.process_manager.cpu_list[i].process.pid == i + 2

        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False

    def test_use_cpu_when_already_using_cpu(self, game):
        process = Process(1, game)

        process.use_cpu()
        process.use_cpu()

        assert process.has_cpu == True
        assert game.process_manager.cpu_list[0].process == process
        for i in range(1, game.config['num_cpus']):
            assert game.process_manager.cpu_list[i].process == None

        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False

    def test_yield_cpu(self, game):
        process = Process(1, game)

        for i in range(0, game.config['num_cpus'] - 1):
            game.process_manager.cpu_list[i].process = Process(i + 2, game)

        process.use_cpu()

        process.yield_cpu()
        assert process.has_cpu == False
        for i in range(0, game.config['num_cpus'] - 1):
            assert game.process_manager.cpu_list[i].process.pid == i + 2
        assert game.process_manager.cpu_list[3].process == None

        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False

    def test_yield_cpu_when_already_idle(self, game):
        process = Process(1, game)

        process.yield_cpu()
        assert process.has_cpu == False
        for i in range(0, game.config['num_cpus']):
            assert game.process_manager.cpu_list[i].process == None

        assert process.is_waiting_for_io == False
        assert process.is_waiting_for_page == False
        assert process.is_blocked == False
        assert process.has_ended == False

    def test_toggle(self, game):
        process = Process(1, game)

        process.toggle()
        assert process.has_cpu == True

        process.toggle()
        assert process.has_cpu == False

    def test_unstarvation(self, game):
        process = Process(1, game)

        current_time = 0

        for i in range(1, LAST_ALIVE_STARVATION_LEVEL):
            current_time += self.starvation_interval
            process.update(current_time, [])

        process.use_cpu()
        assert process.starvation_level == LAST_ALIVE_STARVATION_LEVEL

        current_time += self.time_to_unstarve
        process.update(current_time, [])
        assert process.starvation_level == 0

    def test_use_cpu_min_page_creation(self, game, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        process = Process(1, game)

        with pytest.raises(KeyError):
            game.page_manager.get_page(1, 0)

        process.use_cpu()

        assert game.page_manager.get_page(1, 0).pid == 1
        for i in range(1, MAX_PAGES_PER_PROCESS):
            with pytest.raises(KeyError):
                game.page_manager.get_page(1, i)

    def test_use_cpu_max_page_creation(self, game, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, game)

        with pytest.raises(KeyError):
            game.page_manager.get_page(1, 0)

        process.use_cpu()

        for i in range(1, MAX_PAGES_PER_PROCESS):
            assert game.page_manager.get_page(1, i).pid == 1
        with pytest.raises(KeyError):
            game.page_manager.get_page(1, 4)

    def test_use_cpu_when_already_has_pages(self, game, monkeypatch):
        process = Process(1, game)

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)
        process.use_cpu()

        process.yield_cpu()

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)
        process.use_cpu()

        assert game.page_manager.get_page(1, 0).pid == 1
        for i in range(1, MAX_PAGES_PER_PROCESS):
            with pytest.raises(KeyError):
                game.page_manager.get_page(1, i)

    def test_use_cpu_sets_pages_to_in_use(self, game, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, game)

        process.use_cpu()
        for i in range(0, MAX_PAGES_PER_PROCESS):
            assert game.page_manager.get_page(1, i).in_use == True

        process.yield_cpu()
        process.use_cpu()
        for i in range(0, MAX_PAGES_PER_PROCESS):
            assert game.page_manager.get_page(1, i).in_use == True

    def test_yield_cpu_sets_pages_to_not_in_use(self, game, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, game)

        process.use_cpu()
        process.yield_cpu()

        for i in range(0, MAX_PAGES_PER_PROCESS):
            assert game.page_manager.get_page(1, i).in_use == False

    def test_set_page_to_swap_while_running(self, game, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, game)

        process.use_cpu()

        game.page_manager.get_page(1, 0).swap()
        assert game.page_manager.get_page(1, 0).in_swap == True

        process.update(0, [])

        assert process.is_blocked == True
        assert process.is_waiting_for_page == True
        assert process.is_waiting_for_io == False

    def test_set_page_to_swap_before_running(self, game, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, game)

        process.use_cpu()
        process.yield_cpu()

        game.page_manager.get_page(1, 0).swap()
        assert game.page_manager.get_page(1, 0).in_swap == True

        process.use_cpu()

        process.update(0, [])

        assert process.is_blocked == True
        assert process.is_waiting_for_page == True
        assert process.is_waiting_for_io == False

    def test_remove_page_from_swap_while_running(self, game, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, game)

        process.use_cpu()

        game.page_manager.get_page(1, 0).swap()
        process.update(0, [])
        assert process.is_blocked == True

        game.page_manager.get_page(1, 0).swap()
        process.update(0, [])

        assert process.is_blocked == False
        assert process.is_waiting_for_page == False
        assert process.is_waiting_for_io == False

    def test_yield_cpu_while_waiting_for_page(self, game, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        process = Process(1, game)

        process.use_cpu()

        game.page_manager.get_page(1, 0).swap()
        process.update(0, [])
        assert process.is_waiting_for_page == True

        process.yield_cpu()
        process.update(0, [])

        assert process.is_blocked == False
        assert process.is_waiting_for_page == False
        assert process.is_waiting_for_io == False

    def test_starvation_while_waiting_for_page(self, game, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)
        monkeypatch.setattr(game.process_manager, 'terminate_process', lambda process, by_user: True)
        monkeypatch.setattr(game.process_manager, 'del_process', lambda process: None)

        process = Process(1, game)

        process.use_cpu()

        game.page_manager.get_page(1, 0).swap()
        process.update(0, [])
        assert process.is_blocked == True

        for i in range(1, LAST_ALIVE_STARVATION_LEVEL):
            process.update(i * self.starvation_interval, [])
            assert process.starvation_level == i + 1

        process.update(LAST_ALIVE_STARVATION_LEVEL * self.starvation_interval, [])
        assert process.starvation_level == DEAD_STARVATION_LEVEL
        assert process.has_ended == True
        