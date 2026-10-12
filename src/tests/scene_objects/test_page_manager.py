import pytest

from constants import PAGES_PER_ROW
from scene_objects.page import Page
from scene_objects.page_slot import PageSlot
from scene_objects.page_manager import PageManager
from config.cpu_config import CpuConfig
from config.stage_config import StageConfig


class TestPageManagerSwapCancellation:
    @pytest.fixture(params=['swap-in', 'swap-out'])
    def swapping_pages(self, stage_custom_config, request):
        stage = stage_custom_config(StageConfig(
            num_ram_rows=1, parallel_swaps=2, swap_delay_ms=100))
        page_manager = stage.page_manager
        ram_pages = [page_manager.create_page(1, idx) for idx in range(PAGES_PER_ROW)]
        if request.param == 'swap-in':
            pages = [page_manager.create_page(2, idx) for idx in range(5)]
            for page in ram_pages:
                page_manager.delete_page(page)
        else:
            pages = ram_pages[:5]
        return page_manager, pages

    @pytest.mark.parametrize('retries', [1, 3])
    def test_requeued_swap_has_one_destination(self, swapping_pages, retries):
        page_manager, pages = swapping_pages
        for blocker in pages[:2]:
            blocker.request_swap()
        page_manager.update(0, [])
        page = pages[2]
        page.request_swap()
        page_manager.update(10, [])
        assert page.swap_requested
        assert not page.swap_in_progress

        for retry in range(retries):
            page.request_swap_cancellation()
            page_manager.update(20 + retry * 20, [])
            page.request_swap()
            page_manager.update(30 + retry * 20, [])

        page_manager.update(100, [])
        page_manager.update(101, [])
        assert page.swap_in_progress
        page_manager.update(201, [])
        assert not page.swap_requested
        assert len([slot for slot in page_manager.children
                    if isinstance(slot, PageSlot) and slot.page is page]) == 1

        page_manager.delete_page(page)
        page_manager.update(202, [])
        assert not any(isinstance(slot, PageSlot) and slot.page is page
                       for slot in page_manager.children)

    def test_requeued_swap_goes_to_back_of_queue(self, swapping_pages):
        page_manager, pages = swapping_pages
        for blocker in pages[:2]:
            blocker.request_swap()
        page_manager.update(0, [])
        requeued = pages[2]
        requeued.request_swap()
        page_manager.update(10, [])
        requeued.request_swap_cancellation()
        page_manager.update(20, [])
        for other_page in pages[3:5]:
            other_page.request_swap()
        requeued.request_swap()
        page_manager.update(30, [])

        page_manager.update(100, [])
        page_manager.update(101, [])
        assert pages[3].swap_in_progress
        assert pages[4].swap_in_progress
        assert requeued.swap_requested
        assert not requeued.swap_in_progress

        page_manager.update(201, [])
        page_manager.update(202, [])
        assert requeued.swap_in_progress
        page_manager.update(302, [])
        assert not requeued.swap_requested
        assert len([slot for slot in page_manager.children
                    if isinstance(slot, PageSlot) and slot.page is requeued]) == 1

    def test_deleting_requeued_swap_in_progress_releases_all_slots(self, swapping_pages):
        page_manager, pages = swapping_pages
        page = pages[0]
        page.request_swap()
        page.request_swap_cancellation()
        page.request_swap()
        page_manager.update(0, [])
        assert page.swap_in_progress

        page_manager.delete_page(page)
        page_manager.update(100, [])
        assert not any(isinstance(slot, PageSlot) and slot.page is page
                       for slot in page_manager.children)

    def test_requeue_after_in_progress_cancellation_keeps_fifo_order(self, swapping_pages):
        page_manager, pages = swapping_pages
        for page in pages[:3]:
            page.request_swap()
        page_manager.update(0, [])
        assert pages[0].swap_in_progress
        assert pages[1].swap_in_progress
        assert not pages[2].swap_in_progress

        pages[0].request_swap_cancellation()
        pages[0].request_swap()
        page_manager.update(10, [])
        assert pages[2].swap_in_progress
        assert not pages[0].swap_in_progress

        page_manager.update(110, [])
        page_manager.update(111, [])
        assert pages[0].swap_in_progress
        page_manager.update(211, [])
        assert not pages[0].swap_requested
        assert len([slot for slot in page_manager.children
                    if isinstance(slot, PageSlot) and slot.page is pages[0]]) == 1

class TestPageManager:
    @pytest.fixture
    def stage_config(self):
        return StageConfig(
            cpu_config = CpuConfig(num_cores=4),
            num_ram_rows=1
        )

    @pytest.fixture
    def stage(self, stage_custom_config, stage_config):
        return stage_custom_config(stage_config)

    @pytest.fixture
    def page_manager(self, stage):
        return stage.page_manager

    def test_create_page_in_ram(self, page_manager):
        num_pages = len([child for child in page_manager.children if isinstance(child, Page)])
        assert num_pages == 0

        page1 = page_manager.create_page(5, 0)
        assert page1.pid == 5
        assert page1.idx == 0
        assert not page1.on_disk
        num_pages = len([child for child in page_manager.children if isinstance(child, Page)])
        assert num_pages == 1
        assert page1 == next(child for child in page_manager.children if isinstance(child, Page))

        page2 = page_manager.create_page(5, 1)
        assert page2.pid == 5
        assert page2.idx == 1
        assert not page2.on_disk
        num_pages = len([child for child in page_manager.children if isinstance(child, Page)])
        assert num_pages == 2
        assert page1 in [child for child in page_manager.children if isinstance(child, Page)]
        assert page2 in [child for child in page_manager.children if isinstance(child, Page)]

        page3 = page_manager.create_page(6, 0)
        assert page3.pid == 6
        assert page3.idx == 0
        assert not page3.on_disk
        num_pages = len([child for child in page_manager.children if isinstance(child, Page)])
        assert num_pages == 3
        assert page1 in [child for child in page_manager.children if isinstance(child, Page)]
        assert page2 in [child for child in page_manager.children if isinstance(child, Page)]
        assert page3 in [child for child in page_manager.children if isinstance(child, Page)]

        assert page1.view.y == page2.view.y == page3.view.y
        assert page3.view.x > page2.view.x > page1.view.x

    def test_create_page_on_disk(self, page_manager):
        pages_in_ram = []
        for i in range(PageManager.get_num_cols()):
            pages_in_ram.append(page_manager.create_page(1, i))

        num_pages = len([child for child in page_manager.children if isinstance(child, Page)])
        assert num_pages == PageManager.get_num_cols()

        page1 = page_manager.create_page(2, 0)
        assert page1.pid == 2
        assert page1.idx == 0
        assert page1.on_disk
        num_pages = len([child for child in page_manager.children if isinstance(child, Page)])
        assert num_pages == PageManager.get_num_cols() + 1
        assert page1 == next(child for child in page_manager.children if isinstance(child, Page) and child.on_disk)

        page2 = page_manager.create_page(2, 1)
        assert page2.pid == 2
        assert page2.idx == 1
        assert page2.on_disk
        num_pages = len([child for child in page_manager.children if isinstance(child, Page)])
        assert num_pages == PageManager.get_num_cols() + 2
        assert page1 in [child for child in page_manager.children if isinstance(child, Page) and child.on_disk]
        assert page2 in [child for child in page_manager.children if isinstance(child, Page) and child.on_disk]

        for ram_page in pages_in_ram:
            assert ram_page.view.y < page1.view.y
            assert ram_page.view.y < page2.view.y

        assert page1.view.y == page2.view.y
        assert page2.view.x > page1.view.x

    def test_swap_page(self, page_manager):
        pages = []

        for i in range(PageManager.get_num_cols() * 2):
            pages.append(page_manager.create_page(1, i))

        time = 2000
        page_manager.update(time, [])

        page_manager.swap_page(pages[0])
        assert not pages[0].on_disk
        assert pages[0].swap_requested
        assert not pages[0].swap_in_progress
        time += 1
        page_manager.update(time, [])
        assert not pages[0].on_disk
        assert pages[0].swap_requested
        assert pages[0].swap_in_progress
        time += 1000
        page_manager.update(time, [])
        assert pages[0].on_disk
        assert not pages[0].swap_requested
        assert not pages[0].swap_in_progress
        assert pages[0].view.y > pages[PageManager.get_num_cols()].view.y
        assert pages[0].view.x == pages[PageManager.get_num_cols()].view.x

        page_manager.swap_page(pages[2])
        assert not pages[2].on_disk
        assert pages[2].swap_requested
        assert not pages[2].swap_in_progress
        time += 1
        page_manager.update(time, [])
        assert not pages[2].on_disk
        assert pages[2].swap_requested
        assert pages[2].swap_in_progress
        time += 1000
        page_manager.update(time, [])
        assert pages[2].on_disk
        assert not pages[2].swap_requested
        assert not pages[2].swap_in_progress
        assert pages[2].view.y > pages[PageManager.get_num_cols()].view.y
        assert pages[2].view.x == pages[PageManager.get_num_cols() + 1].view.x

        page_manager.swap_page(pages[2])
        assert pages[2].on_disk
        assert pages[2].swap_requested
        assert not pages[2].swap_in_progress
        time += 1
        page_manager.update(time, [])
        assert pages[2].on_disk
        assert pages[2].swap_requested
        assert pages[2].swap_in_progress
        time += 1000
        page_manager.update(time, [])
        assert not pages[2].on_disk
        assert not pages[2].swap_requested
        assert not pages[2].swap_in_progress
        assert pages[2].view.y == pages[1].view.y
        assert pages[2].view.x < pages[1].view.x

    def test_parallel_swaps(self, stage_custom_config):
        stage_config = StageConfig(
            cpu_config = CpuConfig(num_cores=4),
            num_ram_rows=1,
            swap_delay_ms=1000,
            parallel_swaps=4
        )
        stage = stage_custom_config(stage_config)
        page_manager = PageManager(stage, stage_config)
        page_manager.setup()

        pages = []

        for i in range(24):
            page = page_manager.create_page(1, i)
            pages.append(page)

        time = 10000
        page_manager.update(time, [])

        for i in range(8):
            page_manager.swap_page(pages[i])
            assert pages[i].swap_requested
            assert not pages[i].swap_in_progress
            assert pages[i].in_ram
        for i in range(16, 24):
            page_manager.swap_page(pages[i])
            assert pages[i].swap_requested
            assert not pages[i].swap_in_progress
            assert pages[i].on_disk

        time += 500
        page_manager.update(time, [])

        for i in range(4):
            assert pages[i].swap_in_progress
        for i in range(4, 8):
            assert pages[i].swap_requested
            assert not pages[i].swap_in_progress
        for i in range(8, 16):
            assert not pages[i].swap_requested
            assert not pages[i].swap_in_progress
        for i in range(16, 24):
            assert pages[i].swap_requested
            assert not pages[i].swap_in_progress

        time += 1000
        page_manager.update(time, [])
        time += 500
        page_manager.update(time, [])

        for i in range(4):
            assert not pages[i].swap_requested
            assert pages[i].on_disk
        for i in range(4, 8):
            assert pages[i].swap_requested
            assert not pages[i].swap_in_progress
        for i in range(8, 16):
            assert not pages[i].swap_requested
            assert not pages[i].swap_in_progress
        for i in range(16, 20):
            assert pages[i].swap_in_progress
        for i in range(20, 24):
            assert pages[i].swap_requested
            assert not pages[i].swap_in_progress

        time += 1000
        page_manager.update(time, [])
        time += 500
        page_manager.update(time, [])

        for i in range(4):
            assert not pages[i].swap_requested
            assert pages[i].on_disk
        for i in range(4, 8):
            assert pages[i].swap_in_progress
        for i in range(8, 16):
            assert not pages[i].swap_requested
            assert not pages[i].swap_in_progress
        for i in range(16, 20):
            assert not pages[i].swap_requested
            assert pages[i].in_ram
        for i in range(20, 24):
            assert pages[i].swap_requested
            assert not pages[i].swap_in_progress

        time += 1000
        page_manager.update(time, [])
        time += 500
        page_manager.update(time, [])

        for i in range(4):
            assert not pages[i].swap_requested
            assert pages[i].on_disk
        for i in range(4, 8):
            assert not pages[i].swap_requested
            assert pages[i].on_disk
        for i in range(8, 16):
            assert not pages[i].swap_requested
            assert not pages[i].swap_in_progress
        for i in range(16, 20):
            assert not pages[i].swap_requested
            assert pages[i].in_ram
        for i in range(20, 24):
            assert pages[i].swap_in_progress

        time += 1000
        page_manager.update(time, [])
        time += 500
        page_manager.update(time, [])

        for i in range(4):
            assert not pages[i].swap_requested
            assert pages[i].on_disk
        for i in range(4, 8):
            assert not pages[i].swap_requested
            assert pages[i].on_disk
        for i in range(8, 16):
            assert not pages[i].swap_requested
            assert not pages[i].swap_in_progress
        for i in range(16, 20):
            assert not pages[i].swap_requested
            assert pages[i].in_ram
        for i in range(20, 24):
            assert not pages[i].swap_requested
            assert pages[i].in_ram

    def test_swap_whole_row(self, stage_config, page_manager):
        pages = []

        for i in range(PageManager.get_num_cols() * 2):
            pages.append(page_manager.create_page(1, i))

        time = 10000
        page_manager.update(time, [])

        page_manager.swap_page(pages[0], swap_whole_row=True)

        for i in range(PageManager.get_num_cols()):
            time += 1
            page_manager.update(time, [])
            time += stage_config.swap_delay_ms
            page_manager.update(time, [])
            assert pages[i].on_disk
            assert pages[i].view.x == pages[PageManager.get_num_cols() + i].view.x
            assert pages[i].view.y > pages[PageManager.get_num_cols() + i].view.y

        new_page = page_manager.create_page(2, 0)
        assert not new_page.on_disk

        old_y = pages[0].view.y
        page_manager.swap_page(pages[0], swap_whole_row=True)

        for i in range(PageManager.get_num_cols() - 1):
            time += 1
            page_manager.update(time, [])
            time += stage_config.swap_delay_ms
            page_manager.update(time, [])
            assert not pages[i].on_disk
            assert pages[i].view.x == pages[PageManager.get_num_cols() + i + 1].view.x
            assert pages[i].view.y == new_page.view.y

        assert pages[PageManager.get_num_cols() - 1].on_disk
        assert pages[PageManager.get_num_cols() - 1].view.x == pages[PageManager.get_num_cols() - 1].view.x
        assert pages[PageManager.get_num_cols() - 1].view.y == old_y

    def test_cancel_page_swap(self, page_manager, monkeypatch):
        cancel_called = False

        def cancel_swap_mock():
            nonlocal cancel_called
            cancel_called = True

        page = page_manager.create_page(1, 0)
        monkeypatch.setattr(page, 'cancel_swap', cancel_swap_mock)

        page_manager.swap_page(page)
        assert page.swap_requested
        assert not cancel_called

        page_manager.cancel_page_swap(page)
        assert cancel_called

    def test_cancel_page_swap_for_whole_row(self, page_manager, monkeypatch):
        pages = []

        cancel_calls =  0

        def cancel_swap_mock():
            nonlocal cancel_calls
            cancel_calls += 1

        for i in range(PAGES_PER_ROW * 2):
            page = page_manager.create_page(1, i)
            monkeypatch.setattr(page, 'cancel_swap', cancel_swap_mock)
            page.request_swap()
            assert page.swap_requested
            pages.append(page)

        page_manager.cancel_page_swap(pages[0], cancel_whole_row=True)
        assert cancel_calls == PAGES_PER_ROW

    def test_delete_page_in_ram(self, page_manager):
        pages = []

        for i in range(PageManager.get_num_cols() * 2):
            pages.append(page_manager.create_page(1, i))

        page_to_delete = pages[1]
        assert not page_to_delete.on_disk

        containing_slot = next((
            child for child in page_manager.children if isinstance(child, PageSlot) and child.page == page_to_delete
        ), None)
        assert containing_slot is not None

        page_manager.delete_page(page_to_delete)

        containing_slot = next((
            child for child in page_manager.children if isinstance(child, PageSlot) and child.page == page_to_delete
        ), None)
        assert containing_slot is None

    def test_delete_page_on_disk(self, page_manager):
        pages = []

        for i in range(PageManager.get_num_cols() * 2):
            pages.append(page_manager.create_page(1, i))

        page_to_delete = pages[PageManager.get_num_cols() + 1]
        assert page_to_delete.on_disk

        containing_slot = next((
            child for child in page_manager.children if isinstance(child, PageSlot) and child.page == page_to_delete
        ), None)
        assert containing_slot is not None

        page_manager.delete_page(page_to_delete)

        containing_slot = next((
            child for child in page_manager.children if isinstance(child, PageSlot) and child.page == page_to_delete
        ), None)
        assert containing_slot is None

    def test_delete_page_does_not_ghost_ram_slot_from_pending_swap_in(self, page_manager):
        # A page queued for swap-in (waiting, not yet started) is deleted while
        # its process is terminated. The pending swap must not later reserve a
        # RAM slot for a page that no longer exists (a ghost slot that never
        # completes and visually appears free).
        ram_pages = []
        for i in range(PageManager.get_num_cols()):
            ram_pages.append(page_manager.create_page(1, i))

        disk_page = page_manager.create_page(2, 0)
        assert disk_page.on_disk

        page_manager.swap_page(disk_page)
        assert disk_page.swap_requested
        assert not disk_page.swap_in_progress

        page_manager.delete_page(disk_page)
        page_manager.delete_page(ram_pages[0])

        page_manager.update(2000, [])

        ghost_slot = next((
            child for child in page_manager.children
            if isinstance(child, PageSlot) and child.page is disk_page
        ), None)
        assert ghost_slot is None

    def test_pending_swap_in_does_not_block_new_swap_after_page_deletion(self, page_manager):
        # Regression for the reported bug: after a process holding a queued
        # swap-in page is terminated (freeing a RAM slot but orphaning the queued
        # entry), clicking another disk page must still swap it into RAM instead
        # of turning TEAL forever ("nothing happens").
        ram_pages = []
        for i in range(PageManager.get_num_cols()):
            ram_pages.append(page_manager.create_page(1, i))

        queued_disk_page = page_manager.create_page(1, PageManager.get_num_cols())
        assert queued_disk_page.on_disk
        other_disk_page = page_manager.create_page(1, PageManager.get_num_cols() + 1)
        assert other_disk_page.on_disk

        page_manager.swap_page(queued_disk_page)
        page_manager.delete_page(queued_disk_page)
        page_manager.delete_page(ram_pages[0])

        page_manager.update(2000, [])

        page_manager.swap_page(other_disk_page)
        assert other_disk_page.swap_requested
        assert not other_disk_page.swap_in_progress

        page_manager.update(2001, [])
        assert other_disk_page.swap_in_progress

        page_manager.update(3000, [])
        assert not other_disk_page.on_disk
        assert not other_disk_page.swap_requested
        assert not other_disk_page.swap_in_progress
