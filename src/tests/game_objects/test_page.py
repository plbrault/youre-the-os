import pytest

from engine.game_event import GameEvent
from engine.game_event_type import GameEventType
from game_objects.page import Page
from game_objects.page_manager import PageManager
from game_objects.page_mouse_drag_action import PageMouseDragAction
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

        page_arg = None
        swap_whole_row_arg = None

        page.request_swap(True)

        assert page_arg == page
        assert swap_whole_row_arg

    def test_request_swap_cancellation(self, page_manager, monkeypatch):
        page_arg = None
        cancel_whole_row_arg = None

        def cancel_swap_mock(page, cancel_whole_row):
            nonlocal page_arg, cancel_whole_row_arg
            page_arg = page
            cancel_whole_row_arg = cancel_whole_row

        monkeypatch.setattr(page_manager, 'cancel_page_swap', cancel_swap_mock)

        page = Page(1, 1, page_manager)

        swapping_from = PageSlot()
        swapping_from.page = page
        page.init_swap(swapping_from)

        assert page.swap_requested

        page.request_swap_cancellation()

        assert page_arg == page
        assert not cancel_whole_row_arg

        page_arg = None
        cancel_whole_row_arg = None

        page.request_swap_cancellation(True)

        assert page_arg == page
        assert cancel_whole_row_arg

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
        assert 0.49 < page.swap_percentage_completed < 0.51
        assert swapping_from.page == page
        assert swapping_to.page == page

        page.update(page_manager.stage.config.swap_delay_ms, [])

        assert not page.swap_requested
        assert not page.swap_in_progress
        assert page.on_disk
        assert page.swap_percentage_completed == 0
        assert not swapping_from.has_page
        assert swapping_to.page == page

    def test_cancel_swap(self, page_manager):
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
        assert page.swap_percentage_completed == 0
        assert swapping_from.page == page

        page.cancel_swap()

        assert not page.swap_requested
        assert not page.swap_in_progress
        assert page.swap_percentage_completed == 0
        assert swapping_from.page == page

        page.init_swap(swapping_from)
        page.start_swap(10000, swapping_to)

        assert page.swap_requested
        assert page.swap_in_progress
        assert page.swap_percentage_completed == 0
        assert swapping_from.page == page
        assert swapping_to.page == page

        page.cancel_swap()

        assert not page.swap_requested
        assert not page.swap_in_progress
        assert page.swap_percentage_completed == 0
        assert swapping_from.page == page
        assert not swapping_to.has_page

        page.init_swap(swapping_from)
        page.start_swap(20000, swapping_to)
        page.update(20000 + page_manager.stage.config.swap_delay_ms // 2, [])

        assert page.swap_requested
        assert page.swap_in_progress
        assert 0.49 < page.swap_percentage_completed < 0.51
        assert swapping_from.page == page
        assert swapping_to.page == page

        page.cancel_swap()

        assert not page.swap_requested
        assert not page.swap_in_progress
        assert page.swap_percentage_completed == 0
        assert swapping_from.page == page
        assert not swapping_to.has_page

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

    def test_click_when_swap_requested(self, page_manager, monkeypatch):
        page_arg = None
        cancel_whole_row_arg = None

        def cancel_swap_mock(page, cancel_whole_row):
            nonlocal page_arg, cancel_whole_row_arg
            page_arg = page
            cancel_whole_row_arg = cancel_whole_row

        monkeypatch.setattr(page_manager, 'cancel_page_swap', cancel_swap_mock)

        page = Page(1, 1, page_manager)

        swapping_from = PageSlot()
        swapping_from.page = page

        page.init_swap(swapping_from)
        assert page.swap_requested

        mouse_click_event = GameEvent(GameEventType.MOUSE_LEFT_CLICK,
                                      {'position': (page.view.x, page.view.y), 'shift': False })
        page.update(1000, [mouse_click_event])

        assert page_arg == page
        assert not cancel_whole_row_arg

    def test_shift_click_when_swap_requested(self, page_manager, monkeypatch):
        page_arg = None
        cancel_whole_row_arg = None

        def cancel_swap_mock(page, cancel_whole_row):
            nonlocal page_arg, cancel_whole_row_arg
            page_arg = page
            cancel_whole_row_arg = cancel_whole_row

        monkeypatch.setattr(page_manager, 'cancel_page_swap', cancel_swap_mock)

        page = Page(1, 1, page_manager)

        swapping_from = PageSlot()
        swapping_from.page = page

        page.init_swap(swapping_from)
        assert page.swap_requested

        mouse_click_event = GameEvent(GameEventType.MOUSE_LEFT_CLICK,
                                        {'position': (page.view.x, page.view.y), 'shift': True })
        page.update(1000, [mouse_click_event])

        assert page_arg == page
        assert cancel_whole_row_arg

    def test_mouse_drag(self, page_manager, monkeypatch):
        swap_args = None
        cancel_args = None

        def swap_page_mock(page, swap_whole_row):
            nonlocal swap_args
            swap_args = (page, swap_whole_row)

        def cancel_swap_mock(page, cancel_whole_row):
            nonlocal cancel_args
            cancel_args = (page, cancel_whole_row)

        monkeypatch.setattr(page_manager, 'swap_page', swap_page_mock)
        monkeypatch.setattr(page_manager, 'cancel_page_swap', cancel_swap_mock)

        assert page_manager.current_mouse_drag_action == None

        page1 = Page(1, 1, page_manager)
        page1.view.set_xy(1000, 500)

        page2 = Page(1, 2, page_manager)
        page2.view.set_xy(1000, 600)

        page3 = Page(1, 3, page_manager)
        page3.view.set_xy(1000, 700)

        mouse_drag_event = GameEvent(GameEventType.MOUSE_MOTION,
                                     {'position': (page1.view.x, page1.view.y), 'shift': False, 'left_button_down': True })
        page1.update(1000, [mouse_drag_event])

        assert page_manager.current_mouse_drag_action == PageMouseDragAction.REQUEST_SWAP
        assert swap_args[0] == page1 and not swap_args[1]
        assert not cancel_args

        swap_args = None

        mouse_drag_event = GameEvent(GameEventType.MOUSE_MOTION,
                                     {'position': (page2.view.x, page2.view.y), 'shift': False, 'left_button_down': True })
        page2.update(1000, [mouse_drag_event])

        assert page_manager.current_mouse_drag_action == PageMouseDragAction.REQUEST_SWAP
        assert swap_args[0] == page2 and not swap_args[1]
        assert not cancel_args

        swap_args = None

        page3.init_swap(PageSlot())
        assert page3.swap_requested

        mouse_drag_event = GameEvent(GameEventType.MOUSE_MOTION,
                                        {'position': (page3.view.x, page3.view.y), 'shift': False, 'left_button_down': True })
        page3.update(1000, [mouse_drag_event])

        assert page_manager.current_mouse_drag_action == PageMouseDragAction.REQUEST_SWAP
        assert not swap_args
        assert not cancel_args

        swap_args = None

        page_manager.current_mouse_drag_action = None

        assert page3.swap_requested

        mouse_drag_event = GameEvent(GameEventType.MOUSE_MOTION,
                                     {'position': (page3.view.x, page3.view.y), 'shift': True, 'left_button_down': True })
        page3.update(2000, [mouse_drag_event])

        assert page_manager.current_mouse_drag_action == PageMouseDragAction.CANCEL_SWAP
        assert not swap_args
        assert cancel_args[0] == page3 and not cancel_args[1]

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
