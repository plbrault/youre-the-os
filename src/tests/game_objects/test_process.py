import pytest

from game_objects.process import Process

class TestProcess:
    @pytest.fixture
    def process(self, game):
        return Process(1, game)

    def test_process(self, process):
        assert process.pid == 1
