from random import randint

from lib.game_object import GameObject
from lib.game_event_type import GameEventType
from game_objects.views.process_view import ProcessView

class Process(GameObject):
    _ANIMATION_SPEED = 5

    def __init__(self, pid, process_manager, page_manager):
        self._pid = pid
        self._process_manager = process_manager
        self._page_manager = page_manager

        self._has_cpu = False
        self._is_blocked = False
        self._has_ended = False
        self._starvation_level = 1

        self._last_update_time = 0
        self._current_state_duration = 0
        
        self._pages = []

        super().__init__(ProcessView(self))

    @property
    def pid(self):
        return self._pid

    @property
    def has_cpu(self):
        return self._has_cpu

    @property
    def is_blocked(self):
        return self._is_blocked

    @property
    def has_ended(self):
        return self._has_ended

    @property
    def starvation_level(self):
        return self._starvation_level

    def _use_cpu(self):
        if not self.has_cpu:
            for cpu in self._process_manager.cpu_list:
                if not cpu.has_process:
                    cpu.process = self
                    self._has_cpu = True
                    self.view.set_target_xy(cpu.view.x, cpu.view.y)
                    break
            if self.has_cpu:
                self._current_state_duration = 0
                for slot in self._process_manager.process_slots:
                    if slot.process == self:
                        slot.process = None
                        break
                if len(self._pages) == 0:
                    for i in range(randint(2, 4)):
                        self._pages.append(self._page_manager.create_page(self._pid))
                for page in self._pages:
                    page.in_use = True

    def _yield_cpu(self):
        if self.has_cpu:
            self._has_cpu = False
            self._current_state_duration = 0
            for cpu in self._process_manager.cpu_list:
                if cpu.process == self:
                    cpu.process = None
                    break
            for page in self._pages:
                page.in_use = False
            if self.has_ended:
                if self.starvation_level == 0:
                    self.view.target_y = -self.view.height
                for page in self._pages:
                    self._page_manager.delete_page(page)
            else:
                for slot in self._process_manager.process_slots:
                    if slot.process is None:
                        slot.process = self
                        self.view.set_target_xy(slot.view.x, slot.view.y)
                        break

    def _wait_for_io(self):
        self._is_blocked = True
        self._current_state_duration = 0
        self._process_manager.io_queue.wait_for_event(self._on_io_event)

    def _on_io_event(self):
        self._is_blocked = False
        self._current_state_duration = 0

    def _terminate_gracefully(self):
        if self._process_manager.terminate_process(self, False):
            self._has_ended = True
            self._is_blocked = False
            self._starvation_level = 0

    def _terminate_by_user(self):
        if self._process_manager.terminate_process(self, True):
            self._has_ended = True
            self._is_blocked = False
            self._starvation_level = 6

    def _check_if_clicked_on(self, event):
        if event.type == GameEventType.MOUSE_LEFT_CLICK:
            return self._view.collides(*event.getProperty('position'))
        return False

    def _on_click(self):
        if self.has_cpu:
            self._yield_cpu()
        else:
            self._use_cpu()

    def update(self, current_time, events):
        for event in events:
            if self._check_if_clicked_on(event):
                self._on_click()

        if not self.has_ended:
            if current_time >= self._last_update_time + 1000:
                self._last_update_time = current_time
                    
                self._current_state_duration += 1

                if self.has_cpu and not self.is_blocked:
                    if randint(1, 20) == 1:
                        self._wait_for_io()
                    elif self._current_state_duration >= 1 and randint(1, 100) == 1:
                        self._terminate_gracefully()
                    elif self._current_state_duration == 5:
                        self._starvation_level = 0

                else:
                    if self._current_state_duration > 0 and self._current_state_duration % 10 == 0:
                        if self._starvation_level < 5:
                            self._starvation_level += 1
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
