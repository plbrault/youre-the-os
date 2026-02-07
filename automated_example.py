"""
Example automation script based on automated_skeleton.py.
"""

from dataclasses import dataclass, field

@dataclass
class Page:
    pid: int
    idx: int
    on_disk: bool
    in_use: bool

    @property
    def key(self):
        return self.pid, self.idx

    def __eq__(self, other: tuple[int, int]):
        return self.key == other

@dataclass
class Process:
    pid: int
    cpu: bool = False
    starvation_level: int = 1
    waiting_for_io: bool = False
    waiting_for_page: bool = False
    has_ended: bool = False
    pages: list = field(default_factory=list)

    @property
    def key(self):
        return self.pid

    def __eq__(self, other: int):
        return self.key == other

    @property
    def is_runnable(self):
        return (
            not self.cpu
            and not self.waiting_for_io
            and not self.waiting_for_page
            and not self.has_ended
        )

@dataclass
class IoQueue:
    io_count: int = 0

class SimpleScheduler:
    processes: dict[int, Process] = {}
    pages: dict[tuple[int, int], Page] = {}
    used_cpus: int = 0
    io_queue: IoQueue = IoQueue()
    _event_queue: list = []

    def __init__(self):
        self.processes = {}
        self.pages = {}
        self.used_cpus = 0
        self.io_queue = IoQueue()
        self._event_queue = []

    def move_page(self, pid, idx):
        self._event_queue.append({
            'type': 'page',
            'pid': pid,
            'idx': idx
        })

    def move_process(self, pid):
        self._event_queue.append({
            'type': 'process',
            'pid': pid
        })

    def do_io(self):
        self._event_queue.append({
            'type': 'io_queue'
        })

    def __call__(self, events: list):
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

    def _update_IO_QUEUE(self, event):
        self.io_queue.io_count = event.io_count

    def _update_PAGE_NEW(self, event):
        page = Page(event.pid, event.idx, event.swap, event.use)
        self.pages[(event.pid, event.idx)] = page
        self.processes[event.pid].pages.append(page)

    def _update_PAGE_USE(self, event):
        self.pages[(event.pid, event.idx)].in_use = event.use

    def _update_PAGE_SWAP(self, event):
        self.pages[(event.pid, event.idx)].on_disk = event.swap

    def _update_PAGE_FREE(self, event):
        page = self.pages.pop((event.pid, event.idx))
        try:
            self.processes[event.pid].pages.remove(page)
        except ValueError:
            pass

    def _update_PROC_NEW(self, event):
        self.processes[event.pid] = Process(event.pid)

    def _update_PROC_CPU(self, event):
        self.processes[event.pid].cpu = event.cpu
        if event.cpu:
            self.used_cpus += 1
        else:
            self.used_cpus -= 1

    def _update_PROC_STARV(self, event):
        self.processes[event.pid].starvation_level = event.starvation_level

    def _update_PROC_WAIT_IO(self, event):
        self.processes[event.pid].waiting_for_io = event.waiting_for_io

    def _update_PROC_WAIT_PAGE(self, event):
        self.processes[event.pid].waiting_for_page = event.waiting_for_page

    def _update_PROC_TERM(self, event):
        self.processes[event.pid].has_ended = True

    def _update_PROC_KILL(self, event):
        proc = self.processes.pop(event.pid)
        for page in proc.pages:
            self.pages.pop(page.key, None)

    def _update_PROC_END(self, event):
        proc = self.processes.pop(event.pid)
        self.used_cpus -= 1
        for page in proc.pages:
            self.pages.pop(page.key, None)

    def schedule(self):
        self._handle_io_queue()
        self._handle_page_swaps()
        self._handle_terminated_processes()
        self._schedule_processes()

    def _handle_io_queue(self):
        while self.io_queue.io_count > 0:
            self.do_io()
            self.io_queue.io_count -= 1

    def _handle_page_swaps(self):
        for proc in self.processes.values():
            if proc.waiting_for_page:
                for page in proc.pages:
                    if page.on_disk:
                        self._make_room_in_ram()
                        self.move_page(page.pid, page.idx)
                        page.on_disk = False
                        break

    def _make_room_in_ram(self):
        for page in self.pages.values():
            if not page.on_disk and not page.in_use:
                self.move_page(page.pid, page.idx)
                page.on_disk = True
                return True
        return False

    def _handle_terminated_processes(self):
        for proc in list(self.processes.values()):
            if proc.has_ended and proc.cpu:
                self.move_process(proc.pid)

    def _schedule_processes(self):
        active_procs = [p for p in self.processes.values() if not p.has_ended]
        
        running = [p for p in active_procs if p.cpu]
        waiting = [p for p in active_procs if not p.cpu 
                   and not p.waiting_for_io and not p.waiting_for_page]
        
        for proc in running[:]:
            if proc.starvation_level == 0:
                self.move_process(proc.pid)
                running.remove(proc)
        
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
