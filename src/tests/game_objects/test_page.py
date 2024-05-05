import pytest

from game_objects.page import Page
from game_objects.page_manager import PageManager

class TestPage:
    @pytest.fixture
    def page_manager(self, game):
        return PageManager(game)

    def test_initial_property_values(self, page_manager):
        page = Page(1, 1, page_manager)
        assert page.pid == 1
        assert page.idx == 1
        assert not page.in_use
        assert not page.in_swap

    def test_in_swap_setter(self, page_manager):
        page = Page(1, 1, page_manager)
        page.in_swap = True
        assert page.in_swap
        page.in_swap = False
        assert not page.in_swap
