from queue import Queue

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
        self._swap_in_queue = Queue()
        self._swap_out_queue = Queue()

        self._pages_in_ram_label_xy = (0, 0)
        self._pages_on_disk_label_xy = None

        super().__init__(PageManagerView(self))

    @classmethod
    def get_total_rows(cls):
        return cls._TOTAL_ROWS

    @classmethod
    def get_num_cols(cls):
        return cls._NUM_COLS

    @property
    def stage(self):
        return self._stage

    @property
    def pages_in_ram_label_xy(self):
        return self._pages_in_ram_label_xy

    @property
    def pages_on_disk_label_xy(self):
        return self._pages_on_disk_label_xy

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
            self._pages_on_disk_label_xy = (
                self._stage.process_manager.view.width,
                164 + num_ram_rows * PageSlot().view.height + num_ram_rows * 5)

            for row in range(num_swap_rows):
                for column in range(num_cols):
                    swap_slot = PageSlot()
                    x = self._stage.process_manager.view.width + \
                        column * ram_slot.view.width + column * 5
                    y = self._pages_on_disk_label_xy[1] + \
                        35 + row * ram_slot.view.height + row * 5
                    swap_slot.view.set_xy(x, y)
                    self._swap_slots.append(swap_slot)
            self.children.extend(self._swap_slots)

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
                    page.on_disk = True
                    page.view.set_xy(swap_slot.view.x, swap_slot.view.y)
                    page_created = True
                    break
        self.children.append(page)
        self._pages[(pid, idx)] = page
        return page

    def swap_page(self, page : Page, swap_whole_row : bool = False):
        if page.swap_requested:
            return

        source_slots = self._swap_slots if page.on_disk else self._ram_slots
        target_slots = self._ram_slots if page.on_disk else self._swap_slots
        swap_queue = self._swap_in_queue if page.on_disk else self._swap_out_queue

        can_swap_now = False
        swapping_from = next(source_slot for source_slot in source_slots if source_slot.page == page)
        swapping_to = None

        page.init_swap(swapping_from)

        if not [page for page in self._pages.values() if page.swap_requested]:
            swapping_to = next((target_slot for target_slot in target_slots if not target_slot.has_page), None)
            can_swap_now = bool(swapping_to)

        if can_swap_now:
            page.start_swap(self._stage.current_time, swapping_to)
        else:
            swap_queue.put(page)

        if swap_whole_row:
            slots_on_same_row = [
                slot
                for slot in source_slots
                if (
                    slot.view.y == swapping_from.view.y
                    and slot != swapping_from
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

    def _handle_swap_queues(self, current_time):
        swap_in_progress = bool([page for page in self._pages.values() if page.swap_in_progress])
        empty_ram_slot = next((slot for slot in self._ram_slots if not slot.has_page), None)
        empty_disk_slot = next((slot for slot in self._swap_slots if not slot.has_page), None)

        if not swap_in_progress:
            if empty_ram_slot and not self._swap_in_queue.empty():
                page = self._swap_in_queue.get()
                page.start_swap(current_time, empty_ram_slot)
            elif empty_disk_slot and not self._swap_out_queue.empty():
                page = self._swap_out_queue.get()
                page.start_swap(current_time, empty_disk_slot)

    def update(self, current_time, events):
        self._handle_swap_queues(current_time)
        super().update(current_time, events)
