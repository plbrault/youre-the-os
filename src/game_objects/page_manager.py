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
        self._swap_in_waiting_list = []
        self._swap_out_waiting_list = []

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
            if ram_slot.is_available:
                ram_slot.page = page
                page.view.set_xy(ram_slot.view.x, ram_slot.view.y)
                page_created = True
                break
        if not page_created:
            for swap_slot in self._swap_slots:
                if swap_slot.is_available:
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

        can_swap = False
        swapping_from = None
        swapping_to = None

        for source_slot in source_slots:
            if source_slot.page == page:
                swapping_from = source_slot
                break
        for target_slot in target_slots:
            if target_slot.is_available:
                can_swap = True
                swapping_to = target_slot
                break
        if not can_swap:
            for target_slot in target_slots:
                if target_slot.page and target_slot.page.swap_requested and not target_slot.incoming_page:
                    can_swap = True
                    swapping_to = target_slot
        if can_swap:
            swapping_to.incoming_page = page
            must_wait = bool([page for page in self._pages.values() if page.swap_requested])
            page.init_swap(swapping_from, swapping_to)
            if must_wait:
                if page.on_disk:
                    self._swap_in_waiting_list.append(page)
                else:
                    self._swap_out_waiting_list.append(page)
            else:
                page.start_swap(self._stage.current_time)

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
                    if slot.page is not None:
                        self.swap_page(slot.page, False)

    def delete_page(self, page):
        for ram_slot in self._ram_slots:
            if ram_slot.page == page:
                ram_slot.page = None
                break
            if ram_slot.incoming_page == page:
                ram_slot.incoming_page = None
        for swap_slot in self._swap_slots:
            if swap_slot.page == page:
                swap_slot.page = None
                break
            if swap_slot.incoming_page == page:
                swap_slot.incoming_page = None
        self.children.remove(page)
        del self._pages[(page.pid, page.idx)]

    def _handle_swap_waiting_lists(self, current_time):
        swap_in_progress = bool([page for page in self._pages.values() if page.swap_in_progress])
        if not swap_in_progress:
            next_page_to_swap_in = next((page for page in self._swap_in_waiting_list if not page.swapping_to.page), None)
            next_page_to_swap_out = next((page for page in self._swap_out_waiting_list if not page.swapping_to.page), None)
            if next_page_to_swap_in:
                next_page_to_swap_in.start_swap(current_time)
                self._swap_in_waiting_list.remove(next_page_to_swap_in)
            elif next_page_to_swap_out:
                next_page_to_swap_out.start_swap(current_time)
                self._swap_out_waiting_list.remove(next_page_to_swap_out)

    def update(self, current_time, events):
        self._handle_swap_waiting_lists(current_time)
        super().update(current_time, events)
