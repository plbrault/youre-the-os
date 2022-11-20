import sys, pygame

from game_objects.cpu import Cpu
from game_objects.io_queue import IoQueue
from game_objects.label import Label
from game_objects.process import Process
from game_objects.process_slot import ProcessSlot
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_20
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self._cpu_list = []
        self._process_slots = []
        self._terminated_process_slots = []
        self._io_queue = IoQueue()
        
        self._next_pid = 1
        self._last_new_process_check = 0

        self._game_objects = []

        self._setup()
        self._main_loop()

    @property
    def cpu_list(self):
        return self._cpu_list

    @property
    def process_slots(self):
        return self._process_slots

    @property
    def terminated_process_slots(self):
        return self._terminated_process_slots

    @property
    def io_queue(self):
        return self._io_queue

    def _setup(self):
        screen_size = 1024, 768
        self._screen = pygame.display.set_mode(screen_size)
     
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
            self.terminated_process_slots.append(process_slot)
        self._game_objects.extend(self.terminated_process_slots)

        for i in range(10):
            pid = self._next_pid
            self._next_pid += 1

            process = Process(pid, self)
            process_slot = self.process_slots[i]
            process_slot.process = process
            process.view.setXY(process_slot.view.x, process_slot.view.y)
            self._game_objects.append(process)

    def _update(self, current_time):
        events = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if (event.button == 1):
                    events.append(GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': event.pos }))

        if current_time > self._last_new_process_check + 30000 and self._next_pid <= 42:
            self._last_new_process_check = current_time
            for process_slot in self.process_slots:
                if process_slot.process is None:
                    new_process = Process(self._next_pid, self)
                    self._next_pid += 1
                    new_process.view.x = process_slot.view.x
                    new_process.view.y = process_slot.view.y
                    process_slot.process = new_process
                    self._game_objects.append(new_process)
                    break

        for game_object in self._game_objects:
            game_object.update(current_time, events)

    def _render(self):
        self._screen.fill(Color.BLACK)

        for game_object in self._game_objects:
            game_object.render(self._screen)

        pygame.display.flip()

    def _main_loop(self):
        while True:
            self._update(pygame.time.get_ticks())
            self._render()        
