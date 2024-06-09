import game_monitor
from engine.game_object import GameObject
from game_objects.views.page_manager_view import PageManagerView
from game_objects.page import Page
from game_objects.page_slot import PageSlot

class PageManager(GameObject):
    _TOTAL_ROWS = 11
    _NUM_COLS = 16

    def __init__(self, stage):
        self._stage = stage

        self._ram_slots = []
        self._swap_slots = []
        self._pages = {}

        self._pages_in_ram_label_xy = (0, 0)
        self._swap_is_enabled = True
        self._pages_in_swap_label_xy = None

        super().__init__(PageManagerView(self))

    @classmethod
    def get_total_rows(cls):
        return cls._TOTAL_ROWS

    @classmethod
    def get_num_cols(cls):
        return cls._NUM_COLS

    @property
    def pages_in_ram_label_xy(self):
        return self._pages_in_ram_label_xy

    @property
    def pages_in_swap_label_xy(self):
        return self._pages_in_swap_label_xy

    def get_page(self, pid, idx):
        return self._pages[(pid, idx)]

    def setup(self):
        self._pages_in_ram_label_xy = (
            self._stage.process_manager.view.width, 120)

        num_ram_rows = self._stage.config.num_ram_rows
        num_swap_rows = self._TOTAL_ROWS - num_ram_rows

        num_cols = PageManager._NUM_COLS

        for row in range(num_ram_rows):
            for column in range(num_cols):
                ram_slot = PageSlot()
                x = self._stage.process_manager.view.width + \
                    column * ram_slot.view.width + column * 5
                y = 155 + row * ram_slot.view.height + row * 5
                ram_slot.view.set_xy(x, y)
                self._ram_slots.append(ram_slot)
        self.children.extend(self._ram_slots)

        if num_swap_rows > 0:
            self._pages_in_swap_label_xy = (
                self._stage.process_manager.view.width,
                164 + num_ram_rows * PageSlot().view.height + num_ram_rows * 5)

            for row in range(num_swap_rows):
                for column in range(num_cols):
                    swap_slot = PageSlot()
                    x = self._stage.process_manager.view.width + \
                        column * ram_slot.view.width + column * 5
                    y = self._pages_in_swap_label_xy[1] + \
                        35 + row * ram_slot.view.height + row * 5
                    swap_slot.view.set_xy(x, y)
                    self._swap_slots.append(swap_slot)
            self.children.extend(self._swap_slots)
        else:
            self._swap_is_enabled = False

    def create_page(self, pid, idx):
        page = Page(pid, idx, self)
        page_created = False
        for ram_slot in self._ram_slots:
            if not ram_slot.has_page:
                ram_slot.page = page
                page.view.set_xy(ram_slot.view.x, ram_slot.view.y)
                page_created = True
                break
        if not page_created:
            for swap_slot in self._swap_slots:
                if not swap_slot.has_page:
                    swap_slot.page = page
                    page.in_swap = True
                    page.view.set_xy(swap_slot.view.x, swap_slot.view.y)
                    page_created = True
                    break
        self.children.append(page)
        self._pages[(pid, idx)] = page
        return page

    def swap_page(self, page : Page, swap_whole_row : bool):
        source_slots = self._swap_slots if page.in_swap else self._ram_slots
        target_slots = self._ram_slots if page.in_swap else self._swap_slots

        can_swap = False
        previous_slot = None

        for ram_slot in target_slots:
            if not ram_slot.has_page:
                can_swap = True
                break
        if can_swap:
            for source_slot in source_slots:
                if source_slot.page == page:
                    source_slot.page = None
                    previous_slot = source_slot
                    break
            for target_slot in target_slots:
                if not target_slot.has_page:
                    target_slot.page = page
                    page.view.set_xy(target_slot.view.x, target_slot.view.y)
                    break
            page.in_swap = not page.in_swap
            game_monitor.notify_page_swap(page.pid, page.idx, page.in_swap)
            if swap_whole_row:
                slots_on_same_row = [
                    slot
                    for slot in source_slots
                    if (
                        slot.view.y == previous_slot.view.y
                        and slot != previous_slot
                    )
                ]
                for slot in slots_on_same_row:
                    if slot.has_page:
                        self.swap_page(slot.page, False)

    def delete_page(self, page):
        for ram_slot in self._ram_slots:
            if ram_slot.page == page:
                ram_slot.page = None
                break
        for swap_slot in self._swap_slots:
            if swap_slot.page == page:
                swap_slot.page = None
                break
        self.children.remove(page)
        del self._pages[(page.pid, page.idx)]
