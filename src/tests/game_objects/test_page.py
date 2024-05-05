import pytest

from engine.game_event import GameEvent
from engine.game_event_type import GameEventType
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

    def test_in_use_setter(self, page_manager):
        page = Page(1, 1, page_manager)
        page.in_use = True
        assert page.in_use
        page.in_use = False
        assert not page.in_use

    def test_swap(self, page_manager, monkeypatch):
        page_arg = None

        def swap_page_mock(page):
            nonlocal page_arg
            page_arg = page

        monkeypatch.setattr(page_manager, 'swap_page', swap_page_mock)

        page = Page(1, 1, page_manager)
        page.swap()

        assert page_arg == page

    def test_click_when_not_in_swap(self, page_manager, monkeypatch):
        page_arg = None

        def swap_page_mock(page):
            nonlocal page_arg
            page_arg = page

        monkeypatch.setattr(page_manager, 'swap_page', swap_page_mock)

        page = Page(1, 1, page_manager)
        page.view.set_xy(1000, 500)

        mouse_click_event = GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': (page.view.x, page.view.y) })
        page.update(1000, [mouse_click_event])
        