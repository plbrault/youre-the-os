from queue import Queue
from typing import Optional

from constants import MAX_RAM_ROWS, PAGES_PER_ROW
from engine.scene_object import SceneObject
from scene_objects.views.page_manager_view import PageManagerView
from scene_objects.page import Page, PageMouseDragAction
from scene_objects.page_slot import PageSlot
from factories.page_factory import PageFactory

class PageManager(SceneObject):
    _TOTAL_ROWS = MAX_RAM_ROWS
    _NUM_COLS = PAGES_PER_ROW

    def __init__(self, stage: 'Stage', stage_config: 'StageConfig'):
        self._stage = stage
        self._stage_config = stage_config
        self._page_factory = PageFactory(stage, stage_config)

        self._ram_slots = []
        self._disk_slots = []
        self._pages = {}
        self._swap_in_queue = Queue()
        self._swap_out_queue = Queue()

        self._pages_in_ram_label_xy = (0, 0)
        self._pages_on_disk_label_xy = None

        self._current_mouse_drag_action: Optional[PageMouseDragAction] = None

        super().__init__(PageManagerView(self))

    @property
    def view_vars(self):
        return {
            'pages_in_ram_label_xy': self._pages_in_ram_label_xy,
            'pages_on_disk_label_xy': self._pages_on_disk_label_xy,
        }

    @classmethod
    def get_total_rows(cls):
        return cls._TOTAL_ROWS

    @classmethod
    def get_num_cols(cls):
        return cls._NUM_COLS

    def get_page(self, pid, idx):
        return self._pages[(pid, idx)]

    @property
    def current_mouse_drag_action(self) -> Optional[PageMouseDragAction]:
        return self._current_mouse_drag_action

    @current_mouse_drag_action.setter
    def current_mouse_drag_action(self, value: Optional[PageMouseDragAction]):
        self._current_mouse_drag_action = value

    def setup(self):
        self._pages_in_ram_label_xy = (
            self._stage.process_manager.view.width, 120)

        num_ram_rows = self._stage_config.num_ram_rows
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
                    disk_slot = PageSlot()
                    x = self._stage.process_manager.view.width + \
                        column * ram_slot.view.width + column * 5
                    y = self._pages_on_disk_label_xy[1] + \
                        35 + row * ram_slot.view.height + row * 5
                    disk_slot.view.set_xy(x, y)
                    self._disk_slots.append(disk_slot)
            self.children.extend(self._disk_slots)

    def create_page(self, pid, idx):
        page = self._page_factory.create_page(pid, idx)
        page_created = False
        for ram_slot in self._ram_slots:
            if not ram_slot.has_page:
                ram_slot.page = page
                page.view.set_xy(ram_slot.view.x, ram_slot.view.y)
                page_created = True
                break
        if not page_created:
            for disk_slot in self._disk_slots:
                if not disk_slot.has_page:
                    disk_slot.page = page
                    page.on_disk = True
                    page.view.set_xy(disk_slot.view.x, disk_slot.view.y)
                    page_created = True
                    break
        self.children.append(page)
        self._pages[(pid, idx)] = page
        return page

    def swap_page(self, page : Page, swap_whole_row : bool = False):
        if page.swap_requested:
            return

        source_slots = self._disk_slots if page.on_disk else self._ram_slots
        swap_queue = self._swap_in_queue if page.on_disk else self._swap_out_queue

        swapping_from = next(
            source_slot for source_slot in source_slots if source_slot.page == page)
        page.init_swap(swapping_from)
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

    def cancel_page_swap(self, page : Page, cancel_whole_row : bool = False):
        if not page.swap_requested:
            return

        if cancel_whole_row:
            slots_on_same_row = [
                slot
                for slot in (self._ram_slots + self._disk_slots)
                if (slot.view.y == page.view.y and slot != page)
            ]
            for slot in slots_on_same_row:
                if slot.has_page:
                    self.cancel_page_swap(slot.page)
        else:
            page.cancel_swap()

    def delete_page(self, page):
        for ram_slot in self._ram_slots:
            if ram_slot.page == page:
                ram_slot.page = None
                break
        for disk_slot in self._disk_slots:
            if disk_slot.page == page:
                disk_slot.page = None
                break
        self.children.remove(page)
        del self._pages[(page.pid, page.idx)]

    def _handle_swap_queues(self, current_time):
        num_swap_ins_in_progress = len([
            page for page in self._pages.values()
                if page.swap_in_progress
                    and page.on_disk
        ])
        num_swap_outs_in_progress = len([
            page for page in self._pages.values()
                if page.swap_in_progress
                    and page.in_ram
        ])

        if num_swap_ins_in_progress < self._stage_config.parallel_swaps:
            newly_in_progress = 0
            while newly_in_progress < self._stage_config.parallel_swaps - num_swap_ins_in_progress:
                empty_ram_slot = next((slot for slot in self._ram_slots if not slot.has_page), None)
                if empty_ram_slot and not self._swap_in_queue.empty():
                    page = self._swap_in_queue.get()
                    if not page.swap_requested: # check if swap was cancelled
                        continue
                    page.start_swap(current_time, empty_ram_slot)
                    newly_in_progress += 1
                else:
                    break
            num_swap_ins_in_progress += newly_in_progress

        if num_swap_ins_in_progress == 0:
            newly_in_progress = 0
            while newly_in_progress < self._stage_config.parallel_swaps - num_swap_outs_in_progress:
                empty_disk_slot = next(
                    (slot for slot in self._disk_slots if not slot.has_page),
                    None)
                if empty_disk_slot and not self._swap_out_queue.empty():
                    page = self._swap_out_queue.get()
                    if not page.swap_requested: # check if swap was cancelled
                        continue
                    page.start_swap(current_time, empty_disk_slot)
                    newly_in_progress += 1
                else:
                    break

    def update(self, current_time, events):
        self._handle_swap_queues(current_time)
        super().update(current_time, events)
