import pytest

from constants import PAGES_PER_ROW
from scene_objects.page import Page
from scene_objects.page_slot import PageSlot
from scene_objects.page_manager import PageManager
from config.stage_config import StageConfig

class TestPageManager:
    @pytest.fixture
    def stage_config(self):
        return StageConfig(
            num_cpus=4,
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
            num_cpus=4,
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
         