from typing import Type
from math import sqrt

from constants import (
    ONE_SECOND, LAST_ALIVE_STARVATION_LEVEL, DEAD_STARVATION_LEVEL, MAX_PAGES_PER_PROCESS
)
import game_monitor
from engine.drawable import Drawable
from engine.game_object import GameObject
from engine.game_event_type import GameEventType
from engine.random import randint
from game_objects.views.process_view import ProcessView

_NEW_PAGE_PROBABILITY_DENOMINATOR = 20
_BLINKING_INTERVAL_MS = 200

class Process(GameObject):
    _ANIMATION_SPEED = 35

    def __init__(self, pid, stage,
                 *, time_between_starvation_levels=10000, view_class: Type[Drawable] = ProcessView):
        self._pid = pid
        self._process_manager = stage.process_manager
        self._page_manager = stage.page_manager
        self._time_between_starvation_levels = time_between_starvation_levels

        self._cpu = None
        self._is_waiting_for_io = False
        self._is_on_io_cooldown = False
        self._is_waiting_for_page = False
        self._has_ended = False
        self._starvation_level = 1

        self._last_update_time = stage.current_time
        self._last_event_check_time = self._last_update_time
        # Last time process state changed between running, idle or blocked
        self._last_state_change_time = self._last_update_time
        self._last_starvation_level_change_time = self._last_update_time

        self._display_blink_color = False

        self._pages = []

        self._io_probability_numerator = int(
            stage.config.io_probability * 100)
        self._graceful_termination_probability_numerator = int(
            stage.config.graceful_termination_probability * 100
        )

        super().__init__(view_class(self))

    @property
    def pid(self):
        return self._pid

    @property
    def time_between_starvation_levels(self):
        return self._time_between_starvation_levels

    @property
    def cpu(self):
        return self._cpu

    @property
    def has_cpu(self):
        return self._cpu is not None

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

    @property
    def current_state_duration(self):
        """Time in milliseconds since process state changed between running, idle or blocked."""
        return self._last_update_time - self._last_state_change_time

    @property
    def current_starvation_level_duration(self):
        """Time in milliseconds since starvation level changed."""
        return self._last_update_time - self._last_starvation_level_change_time

    @property
    def is_progressing_to_happiness(self):
        return (
            self.has_cpu
            and self.starvation_level > 0
            and not self.is_blocked
            and not self.has_ended
        )

    @property
    def sort_key(self):
        """Sort key to be used by the `sort_idle_processes` method in the `ProcessManager` class.

        Returns:
            int: The sort key.
        """
        if self.has_cpu:
            return float('inf')
        if self.is_blocked:
            return (LAST_ALIVE_STARVATION_LEVEL + 1) * 100000
        return int(
            (LAST_ALIVE_STARVATION_LEVEL - self.starvation_level) * 100000
                - (self.current_starvation_level_duration
                   / self.time_between_starvation_levels) * 10000
        )

    @property
    def is_in_motion(self):
        return ((self._view.target_x is not None or self._view.target_y is not None)
            and (self._view.target_x != self._view.x or self._view.target_y != self._view.y))

    def use_cpu(self):
        if not self.has_cpu:
            for cpu in self._process_manager.cpu_list:
                if not cpu.has_process:
                    cpu.process = self
                    self._cpu = cpu
                    self.view.set_target_xy(cpu.view.x, cpu.view.y)
                    game_monitor.notify_process_cpu(self._pid, self.has_cpu)
                    break
            if self.has_cpu:
                self._last_state_change_time = self._last_update_time
                for slot in self._process_manager.process_slots:
                    if slot.process == self:
                        slot.process = None
                        break
                if len(self._pages) == 0:
                    # Generate a number of pages between 1 and 4 with a higher
                    # probability for higher numbers
                    num_pages = round(sqrt(randint(1, 20)))
                    for i in range(num_pages):
                        page = self._page_manager.create_page(self._pid, i)
                        self._pages.append(page)
                        game_monitor.notify_page_new(page.pid, page.idx, page.in_swap, page.in_use)
                for page in self._pages:
                    page.in_use = True
                    game_monitor.notify_page_use(page.pid, page.idx, page.in_use)

    def yield_cpu(self):
        if self.has_cpu:
            self._cpu.process = None
            self._cpu = None
            if not self.is_waiting_for_io:
                self._is_on_io_cooldown = False
            if not self.has_ended:
                game_monitor.notify_process_cpu(self._pid, self.has_cpu)
            self._last_state_change_time = self._last_update_time
            for page in self._pages:
                page.in_use = False
                game_monitor.notify_page_use(page.pid, page.idx, page.in_use)
            if self.has_ended:
                if self.starvation_level == 0:
                    self.view.target_y = -self.view.height
                for page in self._pages:
                    game_monitor.notify_page_free(page.pid, page.idx)
                    self._page_manager.delete_page(page)
                self._process_manager.del_process(self)
                game_monitor.notify_process_end(self.pid)
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
            self._last_state_change_time = self._last_update_time

    def _set_waiting_for_io(self, waiting_for_io):
        def update_fn():
            self._is_waiting_for_io = waiting_for_io
        self._update_blocking_condition(update_fn)

    def _set_waiting_for_page(self, waiting_for_page):
        def update_fn():
            self._is_waiting_for_page = waiting_for_page
        if waiting_for_page != self.is_waiting_for_page:
            game_monitor.notify_process_wait_page(self.pid, waiting_for_page)
        self._update_blocking_condition(update_fn)

    def _wait_for_io(self):
        self._set_waiting_for_io(True)
        self._is_on_io_cooldown = True
        self._process_manager.io_queue.wait_for_event(self._on_io_event)
        game_monitor.notify_process_wait_io(self.pid, self.is_waiting_for_io)

    def _on_io_event(self):
        if self.has_ended:
            return
        self._set_waiting_for_io(False)
        game_monitor.notify_process_wait_io(self.pid, self.is_waiting_for_io)

    def _terminate_gracefully(self):
        if self._process_manager.terminate_process(self, False):
            game_monitor.notify_process_terminated(self._pid)
            self._has_ended = True
            self._set_waiting_for_io(False)
            self._set_waiting_for_page(False)
            self._starvation_level = 0

    def _terminate_by_user(self):
        if self._process_manager.terminate_process(self, True):
            self._has_ended = True
            self._set_waiting_for_io(False)
            self._set_waiting_for_page(False)
            self._starvation_level = DEAD_STARVATION_LEVEL
            for page in self._pages:
                game_monitor.notify_page_free(page.pid, page.idx)
                self._page_manager.delete_page(page)
            self._process_manager.del_process(self)
            game_monitor.notify_process_killed(self._pid)

    def _check_if_clicked_on(self, event):
        if event.type in set([GameEventType.MOUSE_LEFT_CLICK, GameEventType.MOUSE_LEFT_DRAG]):
            return self._view.collides(*event.get_property('position'))
        return False

    def toggle(self):
        if self.starvation_level < DEAD_STARVATION_LEVEL:
            if self.has_cpu:
                self.yield_cpu()
            else:
                self.use_cpu()

    def _on_click(self):
        self.toggle()

    def _handle_events(self, events):
        if not self.is_in_motion:
            for event in events:
                if self._check_if_clicked_on(event):
                    self._on_click()

    def _handle_pages_in_swap(self):
        pages_in_swap = 0
        if self.has_cpu:
            for page in self._pages:
                if page.in_swap:
                    pages_in_swap += 1
        self._set_waiting_for_page(pages_in_swap > 0)

    def _update_starvation_level(self, current_time):
        if self.has_cpu and not self.is_blocked:
            if current_time - self._last_state_change_time >= self.cpu.time_for_process_happiness:
                self._last_starvation_level_change_time = current_time
                self._starvation_level = 0
                game_monitor.notify_process_starvation(self._pid, self._starvation_level)
        elif self.current_starvation_level_duration >= self.time_between_starvation_levels:
            self._last_starvation_level_change_time = current_time
            if self._starvation_level < LAST_ALIVE_STARVATION_LEVEL:
                self._starvation_level += 1
                game_monitor.notify_process_starvation(
                    self._pid, self._starvation_level)
            else:
                self._terminate_by_user()

    def _handle_io_probability(self):
        if self.has_cpu and not self.is_blocked:
            if (
                not self.starvation_level == LAST_ALIVE_STARVATION_LEVEL
                and not self._is_on_io_cooldown
                and randint(1, 100) <= self._io_probability_numerator
            ):
                self._wait_for_io()

    def _handle_new_page_probability(self):
        if self.has_cpu and not self.is_blocked:
            if (
                len(self._pages) < MAX_PAGES_PER_PROCESS
                and randint(1, _NEW_PAGE_PROBABILITY_DENOMINATOR) == 1
            ):
                new_page = self._page_manager.create_page(self._pid, len(self._pages))
                self._pages.append(new_page)
                new_page.in_use = True
                game_monitor.notify_page_new(
                    new_page.pid, new_page.idx, new_page.in_swap, new_page.in_use)

    def _handle_graceful_termination_probability(self, current_time):
        if self.has_cpu and not self.is_blocked:
            if (
                current_time - self._last_state_change_time
                    >= ONE_SECOND
                    and randint(1, 100) <= self._graceful_termination_probability_numerator
            ):
                self._terminate_gracefully()

    def _handle_blinking_animation(self, current_time):
        if self._is_waiting_for_page:
            self._display_blink_color = int(current_time / _BLINKING_INTERVAL_MS) % 2 == 1
        else:
            self._display_blink_color = False

    def update(self, current_time, events):
        self._last_update_time = current_time
        self._handle_events(events)

        if not self.has_ended:
            self._handle_pages_in_swap()
            if current_time >= self._last_event_check_time + ONE_SECOND:
                self._last_event_check_time = current_time
                self._update_starvation_level(current_time)
                self._handle_io_probability()
                self._handle_new_page_probability()
                self._handle_graceful_termination_probability(current_time)

        self.view.move_towards_target_xy(self._ANIMATION_SPEED)
        self._handle_blinking_animation(current_time)
