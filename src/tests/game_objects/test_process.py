import pytest

from game_objects.process import Process

class TestProcess:
    def test_constructor(self):
        p = Process()
        assert p is not None