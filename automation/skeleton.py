"""Skeleton for automation script

This is a minimal template that imports the automation API
and provides a skeleton for implementing your own scheduler.

To use:
1. Copy this file anywhere in the project to create your own automation script
2. Implement the schedule() method in the MyScheduler class
3. Run with: pipenv run auto your_script.py

Globals available:
- `num_cpus`: number of available CPUs
- `num_ram_pages`: number of pages that fit on RAM  
- `num_swap_pages`: number of pages that fit on SWAP

See automation/api.py for full documentation of the API.
"""
from automation import RunOs


class MyScheduler(RunOs):
    """Your custom scheduler implementation.
    
    Override the schedule() method to implement your scheduling logic.
    
    Available state:
        self.processes: dict[int, Process] - all active processes
        self.pages: dict[tuple[int,int], Page] - all memory pages
        self.used_cpus: int - number of CPUs currently in use
        self.io_queue.io_count: int - number of I/O events ready
    
    Available actions:
        self.move_process(pid) - toggle process on/off CPU
        self.move_page(pid, idx) - swap page between RAM and disk
        self.do_io() - process one I/O event
    """

    def schedule(self):
        """Implement your scheduling algorithm here.
        
        This method is called once per frame after all game events
        have been processed. Read the current state and use the
        action methods to control the game.
        """
        # TODO: Implement your scheduling logic
        pass


# The game expects a callable named `run_os`
run_os = MyScheduler()
