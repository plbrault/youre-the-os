"""Automation API for You're the OS

This module provides the base classes and infrastructure for creating
automation scripts. It handles:
- Data classes for tracking game state (Process, Page, IoQueue)
- The Scheduler base class with event handling and action dispatching

To create an automation script:
1. Create a subclass of Scheduler
2. Override the schedule() method with your scheduling logic
3. Create an instance and expose it as `scheduler`

Example:
    from automation import Scheduler

    class MyScheduler(Scheduler):
        def schedule(self):
            # Your scheduling logic here
            pass

    scheduler = MyScheduler()

Globals available in automation scripts:
- `num_cpus`: number of available CPUs
- `num_ram_pages`: number of pages that fit on RAM
- `num_swap_pages`: number of pages that fit on SWAP

Event types received:
- 'IO_QUEUE': I/O queue count changed
- 'PAGE_NEW': New memory page created
- 'PAGE_USE': Page use flag changed
- 'PAGE_SWAP_QUEUE': Page queued for swap (or cancelled)
- 'PAGE_SWAP_START': Page swap started
- 'PAGE_SWAP': Page swapped between RAM and disk
- 'PAGE_FREE': Page freed
- 'PROC_NEW': New process created
- 'PROC_CPU': Process moved to/from CPU
- 'PROC_STARV': Process starvation level changed
- 'PROC_WAIT_IO': Process waiting for I/O status changed
- 'PROC_WAIT_PAGE': Process waiting for page status changed
- 'PROC_TERM': Process terminated successfully
- 'PROC_KILL': Process killed (starvation too high)
- 'PROC_END': Terminated process removed from CPU

See `src/game_monitor.py` for more details on events.
"""
from dataclasses import dataclass, field

@dataclass
class Page:
    """Represents a memory page in the game.
    
    Attributes:
        pid: ID of the owner process
        idx: Index of the page within the process (0-based)
        on_disk: True if page is in swap, False if in RAM
        in_use: True if page is currently being used
        waiting_to_swap: True if page is queued for swap but not yet started
        swap_in_progress: True if page is actively being swapped
        swap_percentage_completed: Progress of current swap (0.0 to 1.0)
    """
    pid: int
    idx: int
    on_disk: bool
    in_use: bool
    waiting_to_swap: bool = False
    swap_in_progress: bool = False
    swap_percentage_completed: float = 0.0

    @property
    def key(self):
        """Unique identifier for this page."""
        return self.pid, self.idx

    def __eq__(self, other: tuple[int, int]):
        return self.key == other

@dataclass
class Process:
    """Represents a process in the game.
    
    Attributes:
        pid: Process ID
        has_cpu: True if process is currently on a CPU
        starvation_level: Current starvation level (0=happy, 6=dead)
        waiting_for_io: True if blocked waiting for I/O
        waiting_for_page: True if blocked waiting for a page swap
        has_ended: True if process has terminated
        pages: List of Page objects owned by this process
    """
    pid: int
    has_cpu: bool = False
    starvation_level: int = 1
    waiting_for_io: bool = False
    waiting_for_page: bool = False
    has_ended: bool = False
    pages: list = field(default_factory=list)

    @property
    def key(self):
        """Unique identifier for this process."""
        return self.pid

    def __eq__(self, other: int):
        return self.key == other

@dataclass
class IoQueue:
    """Represents the I/O event queue.
    
    Attributes:
        io_count: Number of I/O events ready to be processed
    """
    io_count: int = 0


class Scheduler:
    """Base class for automation scripts.
    
    This class handles:
    - Receiving events from the game and updating internal state
    - Providing action methods to send commands back to the game
    - Dispatching to event handlers (_update_* methods)
    
    Subclasses should override the schedule() method to implement
    their scheduling algorithm.
    """

    def __init__(self):
        """Initialize the automation state."""
        self.processes: dict[int, Process] = {}
        self.pages: dict[tuple[int, int], Page] = {}
        self.used_cpus: int = 0
        self.io_queue: IoQueue = IoQueue()
        self._event_queue: list = []

    # ==================== Action Methods ====================

    def move_page(self, pid, idx):
        """Request a page swap (RAM <-> disk).
        
        Args:
            pid: Process ID that owns the page
            idx: Index of the page within the process
        """
        self._event_queue.append({
            'type': 'page',
            'pid': pid,
            'idx': idx
        })

    def move_process(self, pid):
        """Toggle a process on/off a CPU.
        
        Args:
            pid: Process ID to move
        """
        self._event_queue.append({
            'type': 'process',
            'pid': pid
        })

    def do_io(self):
        """Process one I/O event from the queue."""
        self._event_queue.append({
            'type': 'io_queue'
        })

    # ==================== Main Entry Point ====================

    def __call__(self, events: list):
        """Entry point called by the game each frame.
        
        Dispatches each event to the appropriate handler,
        then calls schedule() to generate actions.
        
        Args:
            events: List of game events to process
            
        Returns:
            List of action events to send back to the game
        """
        self._event_queue.clear()
        
        # Update internal state from game events
        for event in events:
            handler = getattr(self, f"_update_{event.etype}", None)
            if handler is not None:
                handler(event)
        
        # Run the scheduling algorithm
        self.schedule()
        
        return self._event_queue

    # ==================== Event Handlers ====================
    # These update internal state based on game events.
    # All handlers are defensive - they check if entities exist
    # before updating, since events may arrive for entities
    # that were removed earlier in the same frame.

    def _update_IO_QUEUE(self, event):
        """Handle I/O queue count change.
        
        Args:
            event.io_count: New number of I/O events ready
        """
        self.io_queue.io_count = event.io_count

    def _update_PAGE_NEW(self, event):
        """Handle new page creation.
        
        Args:
            event.pid: Owner process ID
            event.idx: Page index
            event.swap: True if created in swap
            event.use: True if page is in use
        """
        page = Page(event.pid, event.idx, event.swap, event.use)
        self.pages[(event.pid, event.idx)] = page
        proc = self.processes.get(event.pid)
        if proc:
            proc.pages.append(page)

    def _update_PAGE_USE(self, event):
        """Handle page use flag change.
        
        Args:
            event.pid: Owner process ID
            event.idx: Page index
            event.use: New use status
        """
        page = self.pages.get((event.pid, event.idx))
        if page:
            page.in_use = event.use

    def _update_PAGE_SWAP_QUEUE(self, event):
        """Handle page queued for swap (or cancelled).
        
        Args:
            event.pid: Owner process ID
            event.idx: Page index
            event.waiting: True if queued, False if cancelled
        """
        page = self.pages.get((event.pid, event.idx))
        if page:
            page.waiting_to_swap = event.waiting
            if not event.waiting:
                # Swap was cancelled
                page.swap_in_progress = False
                page.swap_percentage_completed = 0.0

    def _update_PAGE_SWAP_START(self, event):
        """Handle page swap started.
        
        Args:
            event.pid: Owner process ID
            event.idx: Page index
        """
        page = self.pages.get((event.pid, event.idx))
        if page:
            page.waiting_to_swap = False
            page.swap_in_progress = True
            page.swap_percentage_completed = 0.0

    def _update_PAGE_SWAP(self, event):
        """Handle page swap completed (RAM <-> disk).
        
        Args:
            event.pid: Owner process ID
            event.idx: Page index
            event.swap: True if now on disk
        """
        page = self.pages.get((event.pid, event.idx))
        if page:
            page.on_disk = event.swap
            page.swap_in_progress = False
            page.swap_percentage_completed = 0.0

    def _update_PAGE_FREE(self, event):
        """Handle page being freed.
        
        Args:
            event.pid: Owner process ID
            event.idx: Page index
        """
        page = self.pages.pop((event.pid, event.idx), None)
        if page:
            proc = self.processes.get(event.pid)
            if proc and page in proc.pages:
                proc.pages.remove(page)

    def _update_PROC_NEW(self, event):
        """Handle new process creation.
        
        Args:
            event.pid: New process ID
        """
        self.processes[event.pid] = Process(event.pid)

    def _update_PROC_CPU(self, event):
        """Handle process moved to/from CPU.
        
        Args:
            event.pid: Process ID
            event.cpu: True if now on CPU
        """
        proc = self.processes.get(event.pid)
        if proc:
            proc.has_cpu = event.cpu
            if event.cpu:
                self.used_cpus += 1
            else:
                self.used_cpus -= 1

    def _update_PROC_STARV(self, event):
        """Handle process starvation level change.
        
        Args:
            event.pid: Process ID
            event.starvation_level: New starvation level (0-6)
        """
        proc = self.processes.get(event.pid)
        if proc:
            proc.starvation_level = event.starvation_level

    def _update_PROC_WAIT_IO(self, event):
        """Handle process I/O wait status change.
        
        Args:
            event.pid: Process ID
            event.waiting_for_io: New wait status
        """
        proc = self.processes.get(event.pid)
        if proc:
            proc.waiting_for_io = event.waiting_for_io

    def _update_PROC_WAIT_PAGE(self, event):
        """Handle process page wait status change.
        
        Args:
            event.pid: Process ID
            event.waiting_for_page: New wait status
        """
        proc = self.processes.get(event.pid)
        if proc:
            proc.waiting_for_page = event.waiting_for_page

    def _update_PROC_TERM(self, event):
        """Handle process termination (ready to be removed).
        
        Args:
            event.pid: Process ID
        """
        proc = self.processes.get(event.pid)
        if proc:
            proc.has_ended = True

    def _update_PROC_KILL(self, event):
        """Handle process killed (starvation too high).
        
        Args:
            event.pid: Process ID
        """
        proc = self.processes.pop(event.pid, None)
        if proc:
            for page in proc.pages:
                self.pages.pop(page.key, None)

    def _update_PROC_END(self, event):
        """Handle terminated process removed from CPU.
        
        Args:
            event.pid: Process ID
        """
        proc = self.processes.pop(event.pid, None)
        if proc:
            self.used_cpus -= 1
            for page in proc.pages:
                self.pages.pop(page.key, None)

    # ==================== Override This ====================

    def schedule(self):
        """Implement your scheduling algorithm here.
        
        This method is called once per frame after all events
        have been processed. Use the action methods (move_page,
        move_process, do_io) to send commands back to the game.
        
        Access self.processes, self.pages, self.io_queue and self.used_cpus for current state.
        """
        pass
