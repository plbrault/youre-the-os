import pygame
import pytest

from scene_objects.io_queue import IoQueue
from ui.color import Color
from window_size import WINDOW_SIZE


class TestIoQueueView:
    @pytest.fixture
    def surface(self):
        return pygame.Surface(WINDOW_SIZE)

    @pytest.fixture
    def io_queue(self):
        return IoQueue(min_waiting_time_ms=1000, max_waiting_time_ms=5000)

    @pytest.fixture
    def view(self, io_queue):
        view = io_queue.view
        view.set_xy(0, 0)
        return view

    def test_draw_renders_idle_queue(self, surface, view):
        view.draw(surface)

        assert surface.get_at((1, 1))[:3] == Color.WHITE

    def test_draw_renders_queue_with_pending_io_events(self, surface, io_queue, view):
        io_queue.wait_for_io_event(0, lambda: None, lambda: True)
        io_queue.update(6000, [])
        view.draw(surface)

        assert surface.get_at((1, 1))[:3] in (Color.WHITE, Color.TEAL)
