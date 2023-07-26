from random import randint

from lib.game_object import GameObject
from game_objects.cpu import Cpu
from game_objects.game_over_dialog import GameOverDialog
from game_objects.io_queue import IoQueue
from game_objects.process import Process
from game_objects.views.process_manager_view import ProcessManagerView
from game_objects.process_slot import ProcessSlot
from lib.ui.fonts import FONT_ARIAL_20

class ProcessManager(GameObject):
    _MAX_PROCESSES = 39
    
    MAX_TERMINATED_BY_USER = 10
    
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
        self._gracefully_terminated_process_count = 0
        self._user_terminated_process_count = 0
        
        self._new_process_probability_numerator = int(game.config['new_process_probability'] * 100)
        self._max_wait_between_new_processes = int(100 / self._new_process_probability_numerator * 1000)
               
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
    
    @property
    def user_terminated_process_count(self):
        return self._user_terminated_process_count
    
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
        
        for i in range(self._game.config['num_cpus']):
            self.cpu_list.append(Cpu(i + 1))
        
        for i, cpu in enumerate(self.cpu_list):
            x = 50 + i * cpu.view.width + i * 5
            y = 50
            cpu.view.set_xy(x, y)
        self.children.extend(self.cpu_list)

        io_queue = self._io_queue
        io_queue.view.set_xy(50, 10)
        self.children.append(io_queue)       

        for row in range(7):
            for column in range(6):
                process_slot = ProcessSlot()          
                x = 50 + column * process_slot.view.width + column * 5
                y = 150 + row * process_slot.view.height + row * 5
                process_slot.view.set_xy(x, y)
                self.process_slots.append(process_slot)
        self.children.extend(self.process_slots)

        for i in range(self.MAX_TERMINATED_BY_USER):
            process_slot = ProcessSlot()
            x = 50 + i * process_slot.view.width + i * 5
            y = 698
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

            process = Process(pid, self._game)
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
            if self._user_terminated_process_count < self.MAX_TERMINATED_BY_USER:
                can_terminate = True

                slot = self._user_terminated_process_slots[self._user_terminated_process_count]
                self._user_terminated_process_count += 1
                slot.process = process
                process.view.set_target_xy(slot.view.x, slot.view.y)

                for cpu in self._cpu_list:
                    if cpu.process == process:
                        cpu.process = None
                for process_slot in self._process_slots:
                    if process_slot.process == process:
                        process_slot.process = None
                
        else:
            can_terminate = True
            self._gracefully_terminated_process_count += 1

        if can_terminate:
            self._alive_process_list.remove(process)

        return can_terminate
    
    def get_current_stats(self):
        process_count_by_starvation_level = [0, 0, 0, 0, 0, 0]
        for process in self._alive_process_list:
            process_count_by_starvation_level[process.starvation_level] += 1
        return {
            'alive_process_count': len(self._alive_process_list),           
            'alive_process_count_by_starvation_level': process_count_by_starvation_level,
            'gracefully_terminated_process_count': self._gracefully_terminated_process_count,
            'user_terminated_process_count': self._user_terminated_process_count,
        }     

    def update(self, current_time, events):
        if self._user_terminated_process_count == self.MAX_TERMINATED_BY_USER:
            processes_are_moving = False
            for child in self.children:
                if isinstance(child, Process):
                    if child.view.target_x is not None and child.view.target_x != child.view.x:
                        processes_are_moving = True
                        break
                    if child.view.target_y is not None and child.view.target_y != child.view.y:
                        processes_are_moving = True
                        break
            if not processes_are_moving:
                self._game.game_over = True
                return
        
        if self._next_pid <= self._game.config['num_processes_at_startup'] and current_time - self._last_new_process_check >= 50:
            self._last_new_process_check = current_time
            self._last_process_creation = current_time
            self._create_process()      
        elif current_time - self._last_new_process_check >= 1000:
            self._last_new_process_check = current_time
            if randint(1, 100) <= self._new_process_probability_numerator or current_time - self._last_process_creation >= self._max_wait_between_new_processes:
                self._create_process()
                self._last_process_creation = current_time
                
        for game_object in self.children:
            game_object.update(current_time, events)
            if isinstance(game_object, Process) and game_object.has_ended and game_object.view.y <= -game_object.view.height:
                self.children.remove(game_object)
                