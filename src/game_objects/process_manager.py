from random import randint

from lib.game_object import GameObject
from game_objects.cpu import Cpu
from game_objects.game_over_dialog import GameOverDialog
from game_objects.io_queue import IoQueue
from game_objects.label import Label
from game_objects.process import Process
from game_objects.views.process_manager_view import ProcessManagerView
from game_objects.process_slot import ProcessSlot
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_20
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType

class ProcessManager(GameObject):
    _MAX_PROCESSES = 42
    
    def __init__(self, game):
        self._game = game
              
        self._cpu_list = None
        self._alive_process_list = None
        self._process_slots = None
        self._user_terminated_process_slots = None
        self._io_queue = None

        self._next_pid = None
        self._last_new_process_check = None
        self._last_process_creation = None
        self._user_terminated_process_count = None
        
        super().__init__(ProcessManagerView(self))
        
        self._setup()

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
        self._user_terminated_process_slots = []
        self._io_queue = IoQueue()
        
        self._next_pid = 1
        self._last_new_process_check = 0
        self._last_process_creation = 0
        self._user_terminated_process_count = 0
        
        self.cpu_list.extend([
            Cpu(1),
            Cpu(2),
            Cpu(3),
            Cpu(4),
        ])
        for i, cpu in enumerate(self.cpu_list):
            x = 50 + i * cpu.view.width + i * 5
            y = 50
            cpu.view.set_xy(x, y)
        self.children.extend(self.cpu_list)

        io_queue = self._io_queue
        io_queue.view.set_xy(50, 10)
        self.children.append(io_queue)       

        processes_label = Label('Processes:')
        processes_label.view.set_xy(50, 120)
        processes_label.font = FONT_ARIAL_20
        self.children.append(processes_label)

        for row in range(7):
            for column in range(6):
                process_slot = ProcessSlot()          
                x = 50 + column * process_slot.view.width + column * 5
                y = 150 + row * process_slot.view.height + row * 5
                process_slot.view.set_xy(x, y)
                self.process_slots.append(process_slot)
        self.children.extend(self.process_slots)

        terminated_processes_label = Label('Terminated By User :')
        terminated_processes_label.view.set_xy(50, 644)
        terminated_processes_label.font = FONT_ARIAL_20
        self.children.append(terminated_processes_label)

        for i in range(5):
            process_slot = ProcessSlot()
            x = 50 + i * process_slot.view.width + i * 5
            y = 644 + terminated_processes_label.view.height + 5
            process_slot.view.set_xy(x, y)
            self._user_terminated_process_slots.append(process_slot)
        self.children.extend(self._user_terminated_process_slots)        

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
            self.children.append(process)
            self._alive_process_list.append(process)

            process.view.set_xy(process_slot.view.x, self.view.height + process.view.height)
            process.view.target_y = process_slot.view.y
            
            return True
        else:
            return False
        
    def terminate_process(self, process, by_user):
        can_terminate = False

        if by_user:
            if self._user_terminated_process_count < 5:
                can_terminate = True

                slot = self._user_terminated_process_slots[self._user_terminated_process_count]
                self._user_terminated_process_count += 1
                slot.process = process
                process.view.set_target_xy(slot.view.x, slot.view.y)

                if self._user_terminated_process_count == 5:
                    self._game.game_over = True

                for cpu in self._cpu_list:
                    if cpu.process == process:
                        cpu.process = None         
        else:
            can_terminate = True

        if can_terminate:
            self._alive_process_list.remove(process) 

        return can_terminate        

    def update(self, current_time, events):
        if self._next_pid <= 12 and current_time - self._last_new_process_check >= 50:
            self._last_new_process_check = current_time
            self._last_process_creation = current_time
            self._create_process()      
        elif current_time - self._last_new_process_check >= 1000:
            self._last_new_process_check = current_time
            if randint(1, 30) == 1 or current_time - self._last_process_creation >= 30000:
                self._create_process()
                self._last_process_creation = current_time
                
        for game_object in self.children:
            game_object.update(current_time, events)
            if isinstance(game_object, Process) and game_object.has_ended and game_object.view.y <= -game_object.view.height:
                self.children.remove(game_object)
                