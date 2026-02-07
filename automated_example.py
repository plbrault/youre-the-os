"""Example automation script with a simple scheduling algorithm.

This script demonstrates how to implement an automated OS scheduler
using the RunOs framework from automation_api.py.

The scheduling algorithm is a simple priority-based scheduler:
1. Process any pending I/O events first
2. Swap in pages that are needed by waiting processes
3. Remove terminated and happy processes from CPUs
4. Schedule processes to CPUs, prioritizing highest starvation

Run with:
    pipenv run auto automated_example.py [--easy|--normal|--hard|--harder|--insane]
"""
import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(abspath(__file__)))

from automation_api import RunOs


class SimpleScheduler(RunOs):
    """A simple OS scheduler implementation.
    
    This scheduler uses a priority-based approach:
    1. Handle I/O events to unblock waiting processes
    2. Swap pages to RAM for processes waiting on pages
    3. Remove happy (starvation=0) processes from CPUs
    4. Schedule highest-starvation processes to available CPUs
    """

    def schedule(self):
        """Main scheduling logic - called each frame."""
        self._handle_io_queue()
        self._handle_page_swaps()
        self._handle_terminated_processes()
        self._schedule_processes()

    def _handle_io_queue(self):
        """Process one I/O event per frame if any are available."""
        if self.io_queue.io_count > 0:
            self.do_io()

    def _handle_page_swaps(self):
        """Swap in pages for processes that are waiting for pages."""
        for proc in self.processes.values():
            if proc.waiting_for_page:
                for page in proc.pages:
                    if page.on_disk:
                        self._make_room_in_ram()
                        self.move_page(page.pid, page.idx)
                        page.on_disk = False
                        break

    def _make_room_in_ram(self):
        """Swap out an unused page from RAM to make room."""
        for page in self.pages.values():
            if not page.on_disk and not page.in_use:
                self.move_page(page.pid, page.idx)
                page.on_disk = True
                return True
        return False

    def _handle_terminated_processes(self):
        """Remove terminated processes from CPU."""
        for proc in list(self.processes.values()):
            if proc.has_ended and proc.cpu:
                self.move_process(proc.pid)

    def _schedule_processes(self):
        """Schedule runnable processes with proper rotation.
        
        Strategy:
        - Remove happy processes (starvation=0) from CPUs immediately
        - Fill empty CPU slots with highest-starvation waiting processes
        """
        active_procs = [p for p in self.processes.values() if not p.has_ended]
        
        running = [p for p in active_procs if p.cpu]
        waiting = [p for p in active_procs if not p.cpu 
                   and not p.waiting_for_io and not p.waiting_for_page]
        
        # Remove happy processes from CPUs immediately
        for proc in running[:]:
            if proc.starvation_level == 0:
                self.move_process(proc.pid)
                running.remove(proc)
        
        # Fill available CPU slots with highest-starvation waiting processes
        waiting.sort(key=lambda p: p.starvation_level, reverse=True)
        available_cpus = num_cpus - len(running)
        
        for proc in waiting:
            if available_cpus <= 0:
                break
            
            pages_on_disk = [p for p in proc.pages if p.on_disk]
            if pages_on_disk:
                # Try to swap in the needed pages
                for page in pages_on_disk:
                    if self._make_room_in_ram():
                        self.move_page(page.pid, page.idx)
                        page.on_disk = False
                continue  # Skip scheduling this process for now

            self.move_process(proc.pid)
            available_cpus -= 1


# Create the run_os callable that the game expects
run_os = SimpleScheduler()
