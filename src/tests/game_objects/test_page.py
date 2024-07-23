import pytest

from engine.game_event import GameEvent
from engine.game_event_type import GameEventType
from game_objects.page import Page
from game_objects.page_manager import PageManager
from game_objects.page_slot import PageSlot

class TestPage:
    @pytest.fixture
    def page_manager(self, stage):
        return PageManager(stage)

    def test_initial_property_values(self, page_manager):
        page = Page(1, 1, page_manager)
        assert page.pid == 1
        assert page.idx == 1
        assert not page.in_use
        assert not page.on_disk

    def test_on_disk_setter(self, page_manager):
        page = Page(1, 1, page_manager)
        page.on_disk = True
        assert page.on_disk
        page.on_disk = False
        assert not page.on_disk

    def test_in_use_setter(self, page_manager):
        page = Page(1, 1, page_manager)
        page.in_use = True
        assert page.in_use
        page.in_use = False
        assert not page.in_use

    def test_request_swap(self, page_manager, monkeypatch):
        page_arg = None
        swap_whole_row_arg = None

        def swap_page_mock(page, swap_whole_row):
            nonlocal page_arg, swap_whole_row_arg
            page_arg = page
            swap_whole_row_arg = swap_whole_row

        monkeypatch.setattr(page_manager, 'swap_page', swap_page_mock)

        page = Page(1, 1, page_manager)
        page.request_swap()

        assert page_arg == page
        assert not swap_whole_row_arg

    def test_swap(self, page_manager):
        page = Page(1, 1, page_manager)

        swapping_from = PageSlot()
        swapping_from.page = page
        swapping_to = PageSlot()

        assert not page.swap_requested
        assert not page.swap_in_progress
        assert not page.on_disk
        assert page.swap_percentage_completed == 0

        page.init_swap(swapping_from)

        assert page.swap_requested
        assert not page.swap_in_progress
        assert not page.on_disk
        assert page.swap_percentage_completed == 0
        assert swapping_from.page == page
        assert swapping_to.page == None

        page.start_swap(0, swapping_to)

        assert page.swap_requested
        assert page.swap_in_progress
        assert not page.on_disk
        assert page.swap_percentage_completed == 0
        assert swapping_from.page == page
        assert swapping_to.page == page

        page.update(page_manager.stage.config.swap_delay_ms // 2, [])

        assert page.swap_requested
        assert page.swap_in_progress
        assert not page.on_disk
        assert page.swap_percentage_completed == 0.5
        assert swapping_from.page == page
        assert swapping_to.page == page

        page.update(page_manager.stage.config.swap_delay_ms, [])

        assert not page.swap_requested
        assert not page.swap_in_progress
        assert page.on_disk
        assert page.swap_percentage_completed == 0
        assert not swapping_from.has_page
        assert swapping_to.page == page

    def test_click_when_not_on_disk(self, page_manager, monkeypatch):
        page_arg = None
        swap_whole_row_arg = None

        def swap_page_mock(page, swap_whole_row):
            nonlocal page_arg, swap_whole_row_arg
            page_arg = page
            swap_whole_row_arg = swap_whole_row

        monkeypatch.setattr(page_manager, 'swap_page', swap_page_mock)

        page = Page(1, 1, page_manager)
        page.view.set_xy(1000, 500)

        mouse_click_event = GameEvent(GameEventType.MOUSE_LEFT_CLICK,
                                      { 'position': (page.view.x, page.view.y), 'shift': False })
        page.update(1000, [mouse_click_event])

        assert page_arg == page
        assert not swap_whole_row_arg

    def test_click_wnen_on_disk(self, page_manager, monkeypatch):
        page_arg = None
        swap_whole_row_arg = None

        def swap_page_mock(page, swap_whole_row):
            nonlocal page_arg, swap_whole_row_arg
            page_arg = page
            swap_whole_row_arg = swap_whole_row

        monkeypatch.setattr(page_manager, 'swap_page', swap_page_mock)

        page = Page(1, 1, page_manager)
        page.on_disk = True
        page.view.set_xy(1000, 500)

        mouse_click_event = GameEvent(GameEventType.MOUSE_LEFT_CLICK,
                                      {'position': (page.view.x, page.view.y), 'shift': False })
        page.update(1000, [mouse_click_event])

        assert page_arg == page
        assert not swap_whole_row_arg

    def test_shift_click_when_not_on_disk(self, page_manager, monkeypatch):
        page_arg = None
        swap_whole_row_arg = None

        def swap_page_mock(page, swap_whole_row):
            nonlocal page_arg, swap_whole_row_arg
            page_arg = page
            swap_whole_row_arg = swap_whole_row

        monkeypatch.setattr(page_manager, 'swap_page', swap_page_mock)

        page = Page(1, 1, page_manager)
        page.view.set_xy(1000, 500)

        mouse_click_event = GameEvent(GameEventType.MOUSE_LEFT_CLICK,
                                      { 'position': (page.view.x, page.view.y), 'shift': True })
        page.update(1000, [mouse_click_event])

        assert page_arg == page
        assert swap_whole_row_arg

    def test_shift_click_wnen_on_disk(self, page_manager, monkeypatch):
        page_arg = None
        swap_whole_row_arg = None

        def swap_page_mock(page, swap_whole_row):
            nonlocal page_arg, swap_whole_row_arg
            page_arg = page
            swap_whole_row_arg = swap_whole_row

        monkeypatch.setattr(page_manager, 'swap_page', swap_page_mock)

        page = Page(1, 1, page_manager)
        page.on_disk = True
        page.view.set_xy(1000, 500)

        mouse_click_event = GameEvent(GameEventType.MOUSE_LEFT_CLICK,
                                      {'position': (page.view.x, page.view.y), 'shift': True })
        page.update(1000, [mouse_click_event])

        assert page_arg == page
        assert swap_whole_row_arg

    def test_blinking_animation(self, page_manager):
        page = Page(1, 1, page_manager)
        page.in_use = True
        page.on_disk = True

        previous_blink_value = page.display_blink_color
        for i in range(1, 5):
            page.update(i * 200, [])
            assert page.display_blink_color != previous_blink_value
            previous_blink_value = page.display_blink_color

    def test_blinking_animation_deactivation_after_stopping_use(self, page_manager):
        page = Page(1, 1, page_manager)
        page.in_use = True
        page.on_disk = True

        page.update(1000, [])
        page.update(1200, [])

        page.in_use = False

        for i in range(1, 5):
            page.update(i * 200, [])
            assert page.display_blink_color == False

    def test_blinking_animation_deactivation_after_removing_from_swap(self, page_manager):
        page = Page(1, 1, page_manager)
        page.in_use = True
        page.on_disk = True

        page.update(1000, [])
        page.update(1200, [])

        page.on_disk = False

        for i in range(1, 5):
            page.update(i * 200, [])
            assert page.display_blink_color == False

    def test_blinking_animation_deactivation_after_removing_from_swap_and_use(self, page_manager):
        page = Page(1, 1, page_manager)
        page.in_use = True
        page.on_disk = True

        page.update(1000, [])
        page.update(1200, [])

        page.on_disk = False
        page.in_use = False

        for i in range(1, 5):
            page.update(i * 200, [])
            assert page.display_blink_color == False
