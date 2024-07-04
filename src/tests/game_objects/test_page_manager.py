import pytest

from game_objects.page import Page
from game_objects.page_slot import PageSlot
from game_objects.page_manager import PageManager
from stage_config import StageConfig

class TestPageManager:
    @pytest.fixture
    def stage_config(self):
        return StageConfig(
            num_cpus=4,
            num_ram_rows=1,
        )

    @pytest.fixture
    def stage(self, stage_custom_config, stage_config):
        return stage_custom_config(stage_config)

    @pytest.fixture
    def page_manager(self, stage):
        page_manager = PageManager(stage)
        page_manager.setup()
        return page_manager

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

    def test_swap_page_when_can_swap(self, page_manager):
        pages = []

        for i in range(PageManager.get_num_cols() * 2):
            pages.append(page_manager.create_page(1, i))

        page_manager.swap_page(pages[0])
        assert pages[0].on_disk
        assert pages[0].view.y > pages[PageManager.get_num_cols()].view.y
        assert pages[0].view.x == pages[PageManager.get_num_cols()].view.x

        page_manager.swap_page(pages[2])
        assert pages[2].on_disk
        assert pages[2].view.y > pages[PageManager.get_num_cols()].view.y
        assert pages[2].view.x == pages[PageManager.get_num_cols() + 1].view.x

        page_manager.swap_page(pages[2])
        assert not pages[2].on_disk
        assert pages[2].view.y == pages[1].view.y
        assert pages[2].view.x < pages[1].view.x

    def test_swap_page_when_cannot_swap(self, page_manager):
        pages = []

        for i in range(PageManager.get_num_cols() * 2):
            pages.append(page_manager.create_page(1, i))

        assert pages[PageManager.get_num_cols()].on_disk

        (old_x, old_y) = (pages[PageManager.get_num_cols()].view.x, pages[PageManager.get_num_cols()].view.y)

        page_manager.swap_page(pages[PageManager.get_num_cols()])

        assert pages[PageManager.get_num_cols()].on_disk
        assert pages[PageManager.get_num_cols()].view.x == old_x
        assert pages[PageManager.get_num_cols()].view.y == old_y

    def test_swap_whole_row(self, page_manager):
        pages = []

        for i in range(PageManager.get_num_cols() * 2):
            pages.append(page_manager.create_page(1, i))

        page_manager.swap_page(pages[0], swap_whole_row=True)

        for i in range(PageManager.get_num_cols()):
            assert pages[i].on_disk
            assert pages[i].view.x == pages[PageManager.get_num_cols() + i].view.x
            assert pages[i].view.y > pages[PageManager.get_num_cols() + i].view.y

        new_page = page_manager.create_page(2, 0)
        assert not new_page.on_disk

        old_y = pages[0].view.y
        page_manager.swap_page(pages[0], swap_whole_row=True)

        for i in range(PageManager.get_num_cols() - 1):
            assert not pages[i].on_disk
            assert pages[i].view.x == pages[PageManager.get_num_cols() + i + 1].view.x
            assert pages[i].view.y == new_page.view.y

        assert pages[PageManager.get_num_cols() - 1].on_disk
        assert pages[PageManager.get_num_cols() - 1].view.x == pages[PageManager.get_num_cols() - 1].view.x
        assert pages[PageManager.get_num_cols() - 1].view.y == old_y

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
         