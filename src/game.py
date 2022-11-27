import os
import pygame
import sys

from game_objects.cpu import Cpu
from game_objects.game_over_dialog import GameOverDialog
from game_objects.io_queue import IoQueue
from game_objects.label import Label
from game_objects.process import Process
from game_objects.process_slot import ProcessSlot
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_20
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType

class Game:
    _MAX_PROCESSES = 42

    def __init__(self):
        pygame.init()
        pygame.font.init()

        self._cpu_list = None
        self._alive_process_list = None
        self._process_slots = None
        self._terminated_process_slots = None
        self._io_queue = None

        self._next_pid = None
        self._last_new_process_check = None
        self._terminated_process_count = None
        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None

        self._window_width = 1024
        self._window_height = 768
        screen_size = self._window_width, self._window_height
        self._screen = pygame.display.set_mode(screen_size)

        icon = pygame.image.load(os.path.join('assets', 'icon.png'))
        pygame.display.set_caption("You're the OS!")
        pygame.display.set_icon(icon)

        self._setup()
        self._main_loop()

    @property
    def cpu_list(self):
        return self._cpu_list

    @property
    def process_slots(self):
        return self._process_slots

    @property
    def io_queue(self):
        return self._io_queue

    def _setup(self):
        self._cpu_list = []
        self._alive_process_list = []
        self._process_slots = []
        self._terminated_process_slots = []
        self._io_queue = IoQueue()
        
        self._next_pid = 1
        self._last_new_process_check = 0
        self._terminated_process_count = 0
        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None

        self._game_objects = []
     
        self.cpu_list.extend([
            Cpu(1),
            Cpu(2),
            Cpu(3),
            Cpu(4),
        ])
        for i, cpu in enumerate(self.cpu_list):
            x = 50 + i * cpu.view.width + i * 5
            y = 50
            cpu.view.setXY(x, y)
        self._game_objects.extend(self.cpu_list)

        io_queue = self._io_queue
        io_queue.view.setXY(50, 10)
        self._game_objects.append(io_queue)       

        processes_label = Label('Processes:')
        processes_label.view.setXY(50, 120)
        processes_label.font = FONT_ARIAL_20
        self._game_objects.append(processes_label)

        for row in range(7):
            for column in range(6):
                process_slot = ProcessSlot()          
                x = 50 + column * process_slot.view.width + column * 5
                y = 150 + row * process_slot.view.height + row * 5
                process_slot.view.setXY(x, y)
                self.process_slots.append(process_slot)
        self._game_objects.extend(self.process_slots)

        terminated_processes_label = Label('Terminated By User :')
        terminated_processes_label.view.setXY(50, 644)
        terminated_processes_label.font = FONT_ARIAL_20
        self._game_objects.append(terminated_processes_label)

        for i in range(5):
            process_slot = ProcessSlot()
            x = 50 + i * process_slot.view.width + i * 5
            y = 644 + terminated_processes_label.view.height + 5
            process_slot.view.setXY(x, y)
            self._terminated_process_slots.append(process_slot)
        self._game_objects.extend(self._terminated_process_slots)

    def _main_loop(self):
        while True:
            self._update(pygame.time.get_ticks())
            self._render()

    def _update(self, current_time):
        events = []

        display_game_over_dialog = self._game_over and self._game_over_time is not None and current_time - self._game_over_time > 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if self._game_over and display_game_over_dialog:
                if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.KEYUP:
                    self._setup()
            elif not self._game_over:
                if event.type == pygame.MOUSEBUTTONUP:
                    if (event.button == 1):
                        events.append(GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': event.pos }))

        if self._game_over:
            if self._game_over_time is None:
                self._game_over_time = current_time
            elif display_game_over_dialog and self._game_over_dialog is None:
                self._game_over_dialog = GameOverDialog()
                self._game_over_dialog.view.setXY(
                    (self._window_width - self._game_over_dialog.view.width) / 2, (self._window_height - self._game_over_dialog.view.height) / 2
                )
                self._game_objects.append(self._game_over_dialog)
        else:
            if current_time > self._last_new_process_check + (30000 if self._next_pid > 12 else 50):
                self._last_new_process_check = current_time
                self._create_process()

        for game_object in self._game_objects:
            game_object.update(current_time, events)

    def _render(self):
        self._screen.fill(Color.BLACK)

        for game_object in self._game_objects:
            game_object.render(self._screen)

        pygame.display.flip()

    def _create_process(self, process_slot_id = None):
        if len(self._alive_process_list) < self._MAX_PROCESSES:
            if process_slot_id is None:
                for i, process_slot in enumerate(self.process_slots):
                    if process_slot.process is None:
                        process_slot_id = id
                        break
            
            pid = self._next_pid
            self._next_pid += 1

            process = Process(pid, self)
            process_slot = self.process_slots[i]
            process_slot.process = process
            self._game_objects.append(process)
            self._alive_process_list.append(process)

            process.view.setXY(process_slot.view.x, self._window_height + process.view.height)
            process.view.target_y = process_slot.view.y
            
            return True
        else:
            return False

    def terminate_process(self, process):
        if self._terminated_process_count < 5:
            terminated_process_slot = self._terminated_process_slots[self._terminated_process_count]
            self._terminated_process_count += 1
            terminated_process_slot.process = process
            process.view.setTargetXY(terminated_process_slot.view.x, terminated_process_slot.view.y)
            for cpu in self._cpu_list:
                if cpu.process == process:
                    cpu.process = None
            if self._terminated_process_count == 5:
                self._game_over = True

            self._alive_process_list.remove(process)

            return True
        else:
            return False
