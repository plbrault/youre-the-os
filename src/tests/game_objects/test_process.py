import pytest

from game_objects.process import Process
from scenes.game import Game

class TestProcess:
    @pytest.fixture
    def ProcessManager(self, monkeypatch):
        pass

    @pytest.fixture
    def process(self, game):
        return Process(1, game)

    def test_initial_property_values(self, process):
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

    def test_starvation_when_idle(self, process):
        process.update(0, [])
        assert process.starvation_level == 1
        process.update(10000, [])
        assert process.starvation_level == 2
        process.update(20000, [])
        assert process.starvation_level == 3
        process.update(40000, [])
        assert process.starvation_level == 4
        process.update(50000, [])
        assert process.starvation_level == 5

        process.update(60000, [])       
