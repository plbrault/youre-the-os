from math import sqrt
from random import randint

from lib.game_object import GameObject
from lib.game_event_type import GameEventType
from game_objects.views.process_view import ProcessView
from lib import event_manager

class Process(GameObject):
    _ANIMATION_SPEED = 35

    Processes = {}

    def __init__(self, pid, game):
        self._pid = pid
        self._process_manager = game.process_manager
        self._page_manager = game.page_manager

        self._has_cpu = False
        self._is_waiting_for_io = False
        self._is_waiting_for_page = False
        self._has_ended = False
        self._starvation_level = 1

        self._last_update_time = 0
        self._current_state_duration = 0

        self._display_blink_color = False

        self._pages = []

        self._io_probability_numerator = int(game.config['io_probability'] * 100)

        super().__init__(ProcessView(self))

    @property
    def pid(self):
        return self._pid

    @property
    def has_cpu(self):
        return self._has_cpu

    @property
    def is_waiting_for_io(self):
        return self._is_waiting_for_io

    @property
    def is_waiting_for_page(self):
        return self._is_waiting_for_page

    @property
    def is_blocked(self):
        return self.is_waiting_for_io or self.is_waiting_for_page

    @property
    def has_ended(self):
        return self._has_ended

    @property
    def starvation_level(self):
        return self._starvation_level

    @property
    def display_blink_color(self):
        return self._display_blink_color

    def _update_blocking_condition(self, update_fn):
        was_blocked = self.is_blocked
        update_fn()
        if was_blocked != self.is_blocked:
            self._current_state_duration = 0

    def _set_waiting_for_io(self, waiting_for_io):
        if self._is_waiting_for_io != waiting_for_io:
            event_manager.event_process_wait_io(self._pid, waiting_for_io)
        def update_fn():
            self._is_waiting_for_io = waiting_for_io
        self._update_blocking_condition(update_fn)

    def _set_waiting_for_page(self, waiting_for_page):
        if self._is_waiting_for_page != waiting_for_page:
            event_manager.event_process_wait_page(self._pid, waiting_for_page)
        def update_fn():
            self._is_waiting_for_page = waiting_for_page
        self._update_blocking_condition(update_fn)

    def use_cpu(self):
        if not self.has_cpu:
            for cpu in self._process_manager.cpu_list:
                if not cpu.has_process:
                    cpu.process = self
                    self._has_cpu = True
                    self.view.set_target_xy(cpu.view.x, cpu.view.y)
                    event_manager.event_process_cpu(self._pid, self._has_cpu)
                    break
            if self.has_cpu:
                self._current_state_duration = 0
                for slot in self._process_manager.process_slots:
                    if slot.process == self:
                        slot.process = None
                        break
                if len(self._pages) == 0:
                    num_pages = round(sqrt(randint(1, 20))) # Generate a number of pages between 1 and 4 with a higher probability for higher numbers
                    for i in range(num_pages):
                        page = self._page_manager.create_page(self._pid, i)
                        self._pages.append(page)
                        event_manager.event_page_new(page.pid, page.idx, page.in_swap, page.in_use)
                for page in self._pages:
                    page.in_use = True
                    event_manager.event_page_use(page.pid, page.idx, page.in_use)

    def yield_cpu(self):
        if self.has_cpu:
            self._has_cpu = False
            event_manager.event_process_cpu(self._pid, self._has_cpu)
            self._current_state_duration = 0
            for cpu in self._process_manager.cpu_list:
                if cpu.process == self:
                    cpu.process = None
                    break
            for page in self._pages:
                page.in_use = False
                event_manager.event_page_use(page.pid, page.idx, page.in_use)
            if self.has_ended:
                if self.starvation_level == 0:
                    self.view.target_y = -self.view.height
                for page in self._pages:
                    event_manager.event_page_free(page.pid, page.idx)
                    self._page_manager.delete_page(page)
                del Process.Processes[self._pid]
            else:
                for slot in self._process_manager.process_slots:
                    if slot.process is None:
                        slot.process = self
                        self.view.set_target_xy(slot.view.x, slot.view.y)
                        break

    def _update_blocking_condition(self, update_fn):
        was_blocked = self.is_blocked
        update_fn()
        if was_blocked != self.is_blocked:
            self._current_state_duration = 0

    def _set_waiting_for_io(self, waiting_for_io):
        def update_fn():
            self._is_waiting_for_io = waiting_for_io
        self._update_blocking_condition(update_fn)

    def _set_waiting_for_page(self, waiting_for_page):
        def update_fn():
            self._is_waiting_for_page = waiting_for_page
        self._update_blocking_condition(update_fn)

    def _wait_for_io(self):
        self._set_waiting_for_io(True)
        self._process_manager.io_queue.wait_for_event(self._on_io_event)

    def _on_io_event(self):
        self._set_waiting_for_io(False)

    def _terminate_gracefully(self):
        if self._process_manager.terminate_process(self, False):
            event_manager.event_process_terminated(self._pid)
            self._has_ended = True
            self._set_waiting_for_io(False)
            self._set_waiting_for_page(False)
            self._starvation_level = 0

    def _terminate_by_user(self):
        if self._process_manager.terminate_process(self, True):
            event_manager.event_process_killed(self._pid)
            self._has_ended = True
            self._set_waiting_for_io(False)
            self._set_waiting_for_page(False)
            self._starvation_level = 6
            for page in self._pages:
                event_manager.event_page_free(page.pid, page.idx)
                self._page_manager.delete_page(page)
            del Process.Processes[self._pid]

    def _check_if_clicked_on(self, event):
        if self.starvation_level >= 6:
            return False
        if event.type == GameEventType.MOUSE_LEFT_CLICK:
            return self._view.collides(*event.getProperty('position'))

        return False

    def onClick(self):
        if self.has_cpu:
            self.yield_cpu()
        else:
            self.use_cpu()

    def update(self, current_time, events):
        for event in events:
            if self._check_if_clicked_on(event):
                self.onClick()

        if not self.has_ended:
            pages_in_swap = 0
            if self.has_cpu:
                for page in self._pages:
                    if page.in_swap:
                        pages_in_swap += 1
            self._set_waiting_for_page(pages_in_swap > 0)

            if current_time >= self._last_update_time + 1000:
                self._last_update_time = current_time

                self._current_state_duration += 1

                if self.has_cpu and not self.is_blocked:
                    if randint(1, 100) <= self._io_probability_numerator:
                        self._wait_for_io()
                    if len(self._pages) < 4 and randint(1, 20) == 1:
                        new_page = self._page_manager.create_page(self._pid, len(self._pages))
                        self._pages.append(new_page)
                        new_page.in_use = True
                        event_manager.event_page_new(page.pid, page.idx, page.in_swap, page.in_use)
                    elif self._current_state_duration >= 1 and randint(1, 100) == 1:
                        self._terminate_gracefully()
                    elif self._current_state_duration == 5:
                        self._starvation_level = 0
                        event_manager.event_process_starvation(self._pid, self._starvation_level)

                else:
                    if self._current_state_duration > 0 and self._current_state_duration % 10 == 0:
                        if self._starvation_level < 5:
                            self._starvation_level += 1
                            event_manager.event_process_starvation(self._pid, self._starvation_level)
                        else:
                            self._terminate_by_user()

        if self.view.target_x is not None:
            if self.view.x == self.view.target_x:
                self.view.target_x = None
            else:
                if self.view.x < self.view.target_x:
                    self.view.x += min(self._ANIMATION_SPEED, self.view.target_x - self.view.x)
                if self.view.x > self.view.target_x:
                    self.view.x -= min(self._ANIMATION_SPEED, self.view.x - self.view.target_x)

        if self.view.target_y is not None:
            if self.view.y == self.view.target_y:
                self.view.target_y = None
            else:
                if self.view.y < self.view.target_y:
                    self.view.y += min(self._ANIMATION_SPEED, self.view.target_y - self.view.y)
                if self.view.y > self.view.target_y:
                    self.view.y -= min(self._ANIMATION_SPEED, self.view.y - self.view.target_y)

        if self._is_waiting_for_page:
            self._display_blink_color = (int(current_time / 200) % 2 == 1)
        else:
            self._display_blink_color = False
