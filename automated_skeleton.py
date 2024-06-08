"""Skeleton for automation script


globals passed are:
`num_cpus` number of available CPUs
`num_ram_pages` number of pages that fit on RAM
`num_swap_pages` number of pages that fit on SWAP


the event type passed are one of the following:
'IO_QUEUE'
'PAGE_NEW'
'PAGE_USE'
'PAGE_SWAP'
'PAGE_FREE'
'PROC_NEW'
'PROC_CPU'
'PROC_STARV'
'PROC_WAIT_IO'
'PROC_WAIT_PAGE'
'PROC_TERM'
'PROC_KILL'
'PROC_END'

a process is identified by its PID

a memory page are identified by the owner's PID
and an index IDX inside the process
(first page is idx=0, second page is idx=1, etc...)

the game expects a callable `run_os`, that takes as argument
the list of events generated by the game objects (processes, pages, etc...)
and expects another list of action events to be returned

see `src/game_monitor.py` for more info on events generated

This skeleton implementation keeps a duplicate state from the game,
it gets updated with each event and then calls the scheduler function
to generate events back to the game
"""
from dataclasses import dataclass, field

#
# A copy of the game's state
#

@dataclass
class Page:
    pid: int
    idx: int
    in_swap: bool
    in_use: bool

    @property
    def key(self):
        return self.pid, self.idx

    def __eq__(self, other: tuple[int,int]):
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

@dataclass
class IoQueue:
    io_count: int = 0


class RunOs:
    """Object oriented skeleton for automation script

    this implements a `__call__` method that should be exposed
    to the game. This method then routes the events to the handlers.

    The handlers should be in the form of `handle_<EVENT_TYPE>`
    (it's similar to http.server.BaseHTTPRequestHandler).

    The helper functions `move_*` and `do_io` will append events
    to the list that shall be sent back to the game.
    """

    # map of processes
    processes: dict[int,Process] = {}

    # map of pages
    pages: dict[tuple[int,int],Page] = {}

    # number of CPUs being used
    used_cpus = 0

    # number of IO events ready
    io_queue = IoQueue()

    _event_queue = []

    def move_page(self, pid, idx):
        """create a move page event"""
        self._event_queue.append({
            'type': 'page',
            'pid': pid,
            'idx': idx
        })

    def move_process(self, pid):
        """create a move process event"""
        self._event_queue.append({
            'type': 'process',
            'pid': pid
        })

    def do_io(self):
        """create a process io event"""
        self._event_queue.append({
            'type': 'io_queue'
        })

    def __call__(self, events: list):
        """Entrypoint from game

        will dispatch each event to the respective handler,
        collecting action events to send back to the game,
        if a handler doesn't exist, will ignore that event.
        """
        self._event_queue.clear()
        # update the status of process/memory
        for event in events:
            handler = getattr(self, f"_update_{event.etype}", None)
            if handler is not None:
                handler(event)
        # run the scheduler
        self.schedule()
        return self._event_queue

    def _update_IO_QUEUE(self, event):
        """IO Queue has new count

        triggered when the IO count in the IO queue has changed

        event:
            .io_count: number of IO waiting to be dispatched
        """
        self.io_queue.io_count = event.io_count

    def _update_PAGE_NEW(self, event):
        """A new memory page was created

        triggered when a process creats a new page, may be in swap

        event:
            .pid: id of the owner process
            .idx: index of page in process
            .swap: bool, if page is in swap
            .use: bool, if page is in use
        """
        page = Page(event.pid, event.idx, event.swap, event.use)
        self.pages[(event.pid, event.idx)] = page
        self.processes[event.pid].pages.append(page)

    def _update_PAGE_USE(self, event):
        """A page 'use' flag has changed

        triggered when either a page was not is use and is now
        in use
        or the page was in use and is now _not_ in use

        this usually comes from a process being moved into or out of
        the CPU

        event:
            .pid: id of the owner process
            .idx: index of page in process
            .use: bool, if page is in use
        """
        self.pages[(event.pid, event.idx)].use = event.use

    def _update_PAGE_SWAP(self, event):
        """A page was swapped

        this happens mostly as a response from a swap request

        event:
            .pid: id of the owner process
            .idx: index of page in process
            .swap: bool, where it is now
        """
        self.pages[(event.pid, event.idx)].swap = event.swap

    def _update_PAGE_FREE(self, event):
        """A page is freed

        this is triggered when a process is terminated

        event:
            .pid: id of the owner process
            .idx: index of page in process
        """
        page = self.pages.pop((event.pid, event.idx))
        try:
            self.processes[event.pid].pages.remove(page)
        except ValueError:
            pass

    def _update_PROC_NEW(self, event):
        """A new process is created

        this happens mostly as the game goes on,
        the initial starvation level is 1 (it starts at 0)

        event:
            .pid: id of the process
        """
        self.processes[event.pid] = Process(event.pid)

    def _update_PROC_CPU(self, event):
        """A process was moved into or out of a CPU

        this happens mostly as a response from a process
        move action

        event:
            .pid: id of the process
            .cpu: bool, if is in CPU or not
        """
        self.processes[event.pid].cpu = event.cpu
        if event.cpu:
            self.used_cpus += 1
        else:
            self.used_cpus -= 1

    def _update_PROC_STARV(self, event):
        """A process' starvation level has changed

        this is either increasing because it doesn't have
        processing time,
        or the process was on the CPU

        event:
            .pid: id of the process
            .starvation_level: the new starvation level
        """
        self.processes[event.pid].starvation_level = event.starvation_level

    def _update_PROC_WAIT_IO(self, event):
        """A process wait (IO) status has changed

        this happens either randomly (blocking)
        or an IO event has been processed

        event:
            .pid: id of the process
            .waiting_for_io: bool, the new waiting status
        """
        self.processes[event.pid].waiting_for_io = event.waiting_for_io

    def _update_PROC_WAIT_PAGE(self, event):
        """A process wait (for PAGE) status has changed

        this happens either because the process was scheduled
        and a memory page is in SWAP (a page can be created into SWAP)
        or it is not longer waiting

        event:
            .pid: id of the process
            .waiting_for_page: bool, the new waiting status
        """
        self.processes[event.pid].waiting_for_page = event.waiting_for_page

    def _update_PROC_TERM(self, event):
        """A process was succesfully terminated

        this happens randomly when a process is in the CPU,

        after being moved from the CPU, the process will disappear

        event:
            .pid: id of the process
        """
        self.processes[event.pid].has_ended = True

    def _update_PROC_KILL(self, event):
        """A process was killed by the user

        this happens if the starvation level is too high (level 5, 0 based)

        the process disappeared from the process list

        event:
            .pid: id of the process
        """
        proc = self.processes.pop(event.pid)
        # shouldn't need this as pages are freed before the process is killed
        for page in proc.pages:
            del self.pages[page.key]

    def _update_PROC_END(self, event):
        """A process was terminated and was gracefully ended

        this happens when a terminated process is removed from CPU

        event:
            .pid: id of the process
        """
        proc = self.processes.pop(event.pid)
        self.used_cpus -= 1
        # shouldn't need this as pages are freed before the process is removed
        for page in proc.pages:
            del self.pages[page.key]

    #
    # implement functions
    #

    def schedule(self):
        """Read current status and update the game"""


#
# the main entrypoint to run the scheduler
#
# it expects a callable `run_os`
#
# it receives a list of events generated from processes/pages
# see `src/game_monitor.py` for generated events
#
# it should return a list of events to happen
#

run_os = RunOs()
