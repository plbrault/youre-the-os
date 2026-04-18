import pygame
import pytest

from engine.modal_view import ModalView
from ui.color import Color
from window_size import WINDOW_SIZE


class StubModalView(ModalView):
    def __init__(self):
        self.draw_content_called = False
        self.draw_content_surface = None
        super().__init__()

    @property
    def width(self):
        return 200

    @property
    def height(self):
        return 100

    def draw_content(self, surface):
        self.draw_content_called = True
        self.draw_content_surface = surface


class TestModalView:
    @pytest.fixture
    def surface(self):
        return pygame.Surface(WINDOW_SIZE)

    @pytest.fixture
    def modal_view(self):
        return StubModalView()

    def test_draw_renders_white_border(self, surface, modal_view):
        modal_view.set_xy(10, 20)
        modal_view.draw(surface)

        # Top edge of outer border should be white
        assert surface.get_at((10 + 50, 20))[:3] == Color.WHITE
        # Bottom edge of outer border should be white
        assert surface.get_at((10 + 50, 20 + 100 - 1))[:3] == Color.WHITE

    def test_draw_renders_gray_background(self, surface, modal_view):
        modal_view.set_xy(10, 20)
        modal_view.draw(surface)

        # Inner body pixel should be gray (70, 70, 70)
        assert surface.get_at((10 + 3, 20 + 3))[:3] == (70, 70, 70)

    def test_draw_calls_draw_content(self, surface, modal_view):
        modal_view.draw(surface)

        assert modal_view.draw_content_called
        assert modal_view.draw_content_surface is surface

    
