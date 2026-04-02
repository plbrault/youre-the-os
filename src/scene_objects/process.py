from enum import Enum, auto
from typing import Type
from math import sqrt

from config.process_config import ProcessConfig
from constants import (
    ONE_SECOND, LAST_ALIVE_STARVATION_LEVEL, DEAD_STARVATION_LEVEL, MAX_PAGES_PER_PROCESS
)
import game_monitor
from engine.drawable import Drawable
from engine.scene_object import SceneObject
from engine.game_event_type import GameEventType
from engine.random import randint
from scene_objects.views.process_view import ProcessView

_NEW_PAGE_PROBABILITY_DENOMINATOR = 20
_BLINKING_INTERVAL_MS = 200

class ProcessState(Enum):
    IDLE = auto()
    RUNNING = auto()
    BLOCKED_ON_CPU_IO_REQUESTED = auto()
    BLOCKED_ON_CPU_IO_AVAILABLE = auto()
    BLOCKED_ON_CPU_PAGE_FAULT = auto()
    BLOCKED_OFF_CPU_IO_REQUESTED = auto()
    BLOCKED_OFF_CPU_IO_AVAILABLE = auto()
    ENDED = auto()

class StateTransition(Enum):
    ASSIGN_TO_CPU = auto()
    TERMINATE_FROM_STARVATION = auto()
    REMOVE_FROM_CPU = auto()
    REQUEST_IO = auto()
    PAGE_FAULT = auto()
    TERMINATE_GRACEFULLY = auto()
    IO_AVAILABLE = auto()
    IO_DELIVERED = auto()
    PAGE_AVAILABLE = auto()

class Process(SceneObject):
    _ANIMATION_SPEED = 35

    _state_transitions = {
        ProcessState.IDLE: {
            StateTransition.ASSIGN_TO_CPU: ProcessState.RUNNING,
            StateTransition.TERMINATE_FROM_STARVATION: ProcessState.ENDED,
        },
        ProcessState.RUNNING: {
            StateTransition.REMOVE_FROM_CPU: ProcessState.IDLE,
            StateTransition.REQUEST_IO: ProcessState.BLOCKED_ON_CPU_IO_REQUESTED,
            StateTransition.PAGE_FAULT: ProcessState.BLOCKED_ON_CPU_PAGE_FAULT,
            StateTransition.TERMINATE_GRACEFULLY: ProcessState.ENDED,
        },
        ProcessState.BLOCKED_ON_CPU_IO_REQUESTED: {
            StateTransition.IO_AVAILABLE: ProcessState.BLOCKED_ON_CPU_IO_AVAILABLE,
            StateTransition.REMOVE_FROM_CPU: ProcessState.BLOCKED_OFF_CPU_IO_REQUESTED,
        },
        ProcessState.BLOCKED_ON_CPU_IO_AVAILABLE: {
            StateTransition.IO_DELIVERED: ProcessState.RUNNING,
            StateTransition.REMOVE_FROM_CPU: ProcessState.BLOCKED_OFF_CPU_IO_AVAILABLE,
            StateTransition.TERMINATE_FROM_STARVATION: ProcessState.ENDED,
        },
        ProcessState.BLOCKED_ON_CPU_PAGE_FAULT: {
            StateTransition.PAGE_AVAILABLE: ProcessState.RUNNING,
            StateTransition.REMOVE_FROM_CPU: ProcessState.IDLE,
            StateTransition.TERMINATE_FROM_STARVATION: ProcessState.ENDED,
        },
        ProcessState.BLOCKED_OFF_CPU_IO_REQUESTED: {
            StateTransition.IO_AVAILABLE: ProcessState.BLOCKED_OFF_CPU_IO_AVAILABLE,
            StateTransition.ASSIGN_TO_CPU: ProcessState.BLOCKED_ON_CPU_IO_REQUESTED,
        },
        ProcessState.BLOCKED_OFF_CPU_IO_AVAILABLE: {
            StateTransition.IO_DELIVERED: ProcessState.IDLE,
            StateTransition.ASSIGN_TO_CPU: ProcessState.BLOCKED_ON_CPU_IO_AVAILABLE,
            StateTransition.TERMINATE_FROM_STARVATION: ProcessState.ENDED,
        },
    }

    def __init__(self, pid: int, stage: 'Stage', config: ProcessConfig,
                 *, view_class: Type[Drawable] = ProcessView):
        self._pid = pid
        self._process_manager = stage.process_manager
        self._cpu_manager = stage.process_manager.cpu_manager
        self._page_manager = stage.page_manager
        self._config = config

        self._cpu = None
        self._state = ProcessState.IDLE
        self._is_on_io_cooldown = False
        self._starvation_level = 1

        self._last_update_time = stage.current_time
        self._last_event_check_time = self._last_update_time
        # Last time process state changed between running, idle or blocked
        self._last_state_change_time = self._last_update_time
        self._last_starvation_level_change_time = self._last_update_time

        self._display_blink_color = False

        self._pages = []

        self._io_probability_numerator = int(
            config.io_probability * 100)
        self._graceful_termination_probability_numerator = int(
            config.graceful_termination_probability * 100
        )

        super().__init__(view_class(self))

    @property
    def pid(self):
        return self._pid

    @property
    def time_between_starvation_levels(self):
        return self._config.time_between_starvation_levels_ms

    @property
    def cpu(self):
        return self._cpu

    @property
    def has_cpu(self):
        return self._cpu is not None

    @property
    def is_waiting_for_io(self):
        return self._state in (
            ProcessState.BLOCKED_ON_CPU_IO_REQUESTED,
            ProcessState.BLOCKED_ON_CPU_IO_AVAILABLE,
            ProcessState.BLOCKED_OFF_CPU_IO_REQUESTED,
            ProcessState.BLOCKED_OFF_CPU_IO_AVAILABLE
        )

    @property
    def is_waiting_for_page(self):
        return self._state == ProcessState.BLOCKED_ON_CPU_PAGE_FAULT

    @property
    def is_blocked(self):
        return self._state in (
            ProcessState.BLOCKED_ON_CPU_IO_REQUESTED,
            ProcessState.BLOCKED_ON_CPU_IO_AVAILABLE,
            ProcessState.BLOCKED_ON_CPU_PAGE_FAULT,
            ProcessState.BLOCKED_OFF_CPU_IO_REQUESTED,
            ProcessState.BLOCKED_OFF_CPU_IO_AVAILABLE
        )

    @property
    def is_running(self):
        return self._state == ProcessState.RUNNING

    @property
    def has_ended(self):
        return self._state == ProcessState.ENDED

    @property
    def has_ended_gracefully(self):
        return self._state == ProcessState.ENDED and self.starvation_level == 0

    @property
    def io_event_arrived(self):
        return self._state in (
            ProcessState.BLOCKED_ON_CPU_IO_AVAILABLE,
            ProcessState.BLOCKED_OFF_CPU_IO_AVAILABLE
        )

    @property
    def state(self):
        return self._state

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
            and self.is_running
        )

    @property
    def time_to_termination(self):
        """Time in milliseconds until process is terminated due to starvation.
        Returns float('inf') if process is currently running, if it is waiting
        for an I/O event that is not yet available, or if it has terminated gracefully.
        Returns 0 if process has already been terminated due to starvation.
        """
        if self.starvation_level >= DEAD_STARVATION_LEVEL:
            return 0
        if self.state in [
            ProcessState.RUNNING,
            ProcessState.BLOCKED_ON_CPU_IO_REQUESTED,
            ProcessState.BLOCKED_OFF_CPU_IO_REQUESTED
        ] or self.has_ended_gracefully:
            return float('inf')
        remaining_starvation_levels = DEAD_STARVATION_LEVEL - self.starvation_level
        remaining_time_for_current_level = (
            self.time_between_starvation_levels - self.current_starvation_level_duration
        )
        time_to_termination = max(
            0,
            (remaining_starvation_levels - 1)
            * self.time_between_starvation_levels + remaining_time_for_current_level
        )
        return time_to_termination

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

    def use_cpu(self, use_e_core=False):
        if not self.has_cpu:
            cpu = self._cpu_manager.select_free_cpu(use_e_core=use_e_core)
            if cpu is not None:
                cpu.process = self
                self._cpu = cpu
                self.apply_state_transition(StateTransition.ASSIGN_TO_CPU)

                self.view.set_target_xy(cpu.view.x, cpu.view.y)
                game_monitor.notify_process_cpu(self._pid, self.has_cpu)

                self._last_state_change_time = self._last_update_time
                for slot in self._process_manager.process_slots:
                    if slot.process == self:
                        slot.process = None
                        break
                if len(self._pages) == 0:
                    num_pages = round(sqrt(randint(1, 20)))
                    for i in range(num_pages):
                        page = self._page_manager.create_page(self._pid, i)
                        self._pages.append(page)
                        game_monitor.notify_page_new(page.pid, page.idx, page.on_disk, page.in_use)
                for page in self._pages:
                    page.in_use = True
                    game_monitor.notify_page_use(page.pid, page.idx, page.in_use)

    def yield_cpu(self):
        if self.has_cpu:
            self._cpu.process = None
            self._cpu = None
            self.apply_state_transition(StateTransition.REMOVE_FROM_CPU)

            if not self.is_waiting_for_io:
                self._is_on_io_cooldown = False
            if not self.has_ended:
                game_monitor.notify_process_cpu(self._pid, self.has_cpu)
            self._last_state_change_time = self._last_update_time
            for page in self._pages:
                page.in_use = False
                game_monitor.notify_page_use(page.pid, page.idx, page.in_use)

            if self.has_ended:
                if self.has_ended_gracefully:
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

    def _update_blocking_condition(self, new_state):
        was_blocked = self.is_blocked
        self._state = new_state
        if was_blocked != self.is_blocked:
            self._last_state_change_time = self._last_update_time

    def _set_unblocked_state(self):
        if self.has_cpu:
            self._update_blocking_condition(ProcessState.RUNNING)
        else:
            self._update_blocking_condition(ProcessState.IDLE)

    def _set_waiting_for_io(self, waiting_for_io):
        if waiting_for_io:
            self._update_blocking_condition(ProcessState.BLOCKED_ON_CPU_IO_REQUESTED)
        elif not self.is_waiting_for_page:
            self._set_unblocked_state()

    def _wait_for_io(self):
        self._update_blocking_condition(ProcessState.BLOCKED_ON_CPU_IO_REQUESTED)
        self._is_on_io_cooldown = True
        self._process_manager.io_queue.wait_for_event(
            self._last_update_time,
            self._on_io_event_arrived,
            self._on_io_event
        )
        game_monitor.notify_process_wait_io(self.pid, self.is_waiting_for_io)

    def _on_io_event_arrived(self, current_time):
        if not self.has_ended:
            self._last_starvation_level_change_time = current_time
            if self.has_cpu:
                self._state = ProcessState.BLOCKED_ON_CPU_IO_AVAILABLE
            else:
                self._state = ProcessState.BLOCKED_OFF_CPU_IO_AVAILABLE

    def _on_io_event(self):
        if self.has_ended:
            return
        self._set_unblocked_state()
        game_monitor.notify_process_wait_io(self.pid, self.is_waiting_for_io)

    def _terminate_gracefully(self):
        if self._process_manager.terminate_process(self, False):
            game_monitor.notify_process_terminated(self._pid)
            self._state = ProcessState.ENDED
            self._last_state_change_time = self._last_update_time
            self._starvation_level = 0

    def _terminate_by_user(self):
        if self._process_manager.terminate_process(self, True):
            self._state = ProcessState.ENDED
            self._last_state_change_time = self._last_update_time
            self._starvation_level = DEAD_STARVATION_LEVEL
            for page in self._pages:
                game_monitor.notify_page_free(page.pid, page.idx)
                self._page_manager.delete_page(page)
            self._process_manager.del_process(self)
            game_monitor.notify_process_killed(self._pid)

    def toggle(self, to_e_core=False):
        if self.starvation_level < DEAD_STARVATION_LEVEL:
            if self.has_cpu and not to_e_core:
                self.yield_cpu()
            else:
                self.use_cpu(use_e_core=to_e_core)

    def _on_left_click(self):
        self.toggle()

    def _on_right_click(self):
        self.toggle(to_e_core=True)

    def _check_if_clicked_on(self, event):
        if (
            event.type == GameEventType.MOUSE_LEFT_CLICK
            or (
                event.type == GameEventType.MOUSE_MOTION
                and event.get_property('left_button_down')
            )
        ):
            if self._view.collides(*event.get_property('position')):
                self._on_left_click()
        elif (
            event.type == GameEventType.MOUSE_RIGHT_CLICK
            or (
                event.type == GameEventType.MOUSE_MOTION
                and event.get_property('right_button_down')
            )
        ):
            if self._view.collides(*event.get_property('position')):
                self._on_right_click()

    def _handle_events(self, events):
        if not self.is_in_motion:
            for event in events:
                self._check_if_clicked_on(event)

    def _handle_pages(self):
        page_fault = any(page for page in self._pages if page.in_use and not page.on_disk and not page.swap_in_progress)
        if self.state == ProcessState.RUNNING and page_fault:
            self.apply_state_transition(StateTransition.PAGE_FAULT)
            game_monitor.notify_process_wait_page(self.pid, True)
            self._last_state_change_time = self._last_update_time
        elif self.state == ProcessState.BLOCKED_ON_CPU_PAGE_FAULT and not page_fault:
            self.apply_state_transition(StateTransition.PAGE_AVAILABLE)
            game_monitor.notify_process_wait_page(self.pid, False)
            self._last_state_change_time = self._last_update_time

    def _update_starvation_level(self, current_time):
        if self.is_running:
            if current_time - self._last_state_change_time >= self.cpu.process_happiness_ms:
                self._last_starvation_level_change_time = current_time
                self._starvation_level = 0
                game_monitor.notify_process_starvation(
                    self._pid, self._starvation_level, self.time_to_termination
                )
        elif self.current_starvation_level_duration >= self.time_between_starvation_levels:
            if self._state == ProcessState.BLOCKED_ON_CPU_IO_REQUESTED:
                return
            self._last_starvation_level_change_time = current_time
            if self._starvation_level < LAST_ALIVE_STARVATION_LEVEL:
                self._starvation_level += 1
                game_monitor.notify_process_starvation(
                    self._pid, self._starvation_level, self.time_to_termination)
            else:
                self._terminate_by_user()

    def _handle_io_probability(self):
        if self.is_running:
            if (
                not self.starvation_level == LAST_ALIVE_STARVATION_LEVEL
                and not self._is_on_io_cooldown
                and randint(1, 100) <= self._io_probability_numerator
            ):
                self._wait_for_io()

    def _handle_new_page_probability(self):
        if self.is_running:
            if (
                len(self._pages) < MAX_PAGES_PER_PROCESS
                and randint(1, _NEW_PAGE_PROBABILITY_DENOMINATOR) == 1
            ):
                new_page = self._page_manager.create_page(self._pid, len(self._pages))
                self._pages.append(new_page)
                new_page.in_use = True
                game_monitor.notify_page_new(
                    new_page.pid, new_page.idx, new_page.on_disk, new_page.in_use)

    def _handle_graceful_termination_probability(self, current_time):
        if self.is_running:
            if (
                current_time - self._last_state_change_time
                    >= ONE_SECOND
                    and randint(1, 100) <= self._graceful_termination_probability_numerator
            ):
                self._terminate_gracefully()

    def _handle_blinking_animation(self, current_time):
        if self.is_waiting_for_page:
            self._display_blink_color = int(current_time / _BLINKING_INTERVAL_MS) % 2 == 1
        else:
            self._display_blink_color = False

    def apply_state_transition(self, transition: StateTransition):
        if self._state in self._state_transitions and transition in Process._state_transitions[self._state]:
            self._state = self._state_transitions[self._state][transition]

    def update(self, current_time, events):
        self._last_update_time = current_time
        self._handle_events(events)
        self._handle_pages()

        if not self.has_ended:
            if current_time >= self._last_event_check_time + ONE_SECOND:
                self._last_event_check_time = current_time
                self._update_starvation_level(current_time)
                self._handle_io_probability()
                self._handle_new_page_probability()
                self._handle_graceful_termination_probability(current_time)

        self.view.move_towards_target_xy(self._ANIMATION_SPEED)
        self._handle_blinking_animation(current_time)
