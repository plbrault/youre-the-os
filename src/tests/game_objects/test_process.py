import pytest

from game_objects.process import Process

class TestProcess:
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

