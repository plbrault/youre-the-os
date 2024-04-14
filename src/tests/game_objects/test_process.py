import pytest

from game_objects.process import Process

class TestProcess:
    @property
    def starvation_interval(self):
        return 10000

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

        for i in range(0, 5):
            process.update(i * self.starvation_interval, [])
            assert process.starvation_level == i + 1

    def test_max_starvation(self, game, monkeypatch):
        monkeypatch.setattr(game.process_manager, 'terminate_process', lambda process, by_user: True)
        monkeypatch.setattr(game.process_manager, 'del_process', lambda process: None)

        process = Process(1, game)

        for i in range(0, 5):
            process.update(i * self.starvation_interval, [])

        assert process.starvation_level == 5

        process.update(6 * self.starvation_interval, [])

        assert process.starvation_level == 6
        assert process.has_ended == True
