from automation import Scheduler

MAX_PROCESS_MOVES_PER_FRAME = 2
MAX_PAGE_SWAPS_PER_FRAME = 4
STARVATION_THRESHOLD_TO_YIELD = 3

class SimpleScheduler(Scheduler):
    def __init__(self):
        super().__init__()
        self._recently_moved_processes = []
        self._recently_moved_window = 3

    def schedule(self):
        self._pending_swap_outs = set()
        self._pending_swap_ins = set()
        self._process_moves_this_frame = 0
        self._page_swaps_this_frame = 0
        self._handle_io_queue()
        self._handle_page_swaps()
        self._handle_terminated_processes()
        self._schedule_processes()
        if len(self._recently_moved_processes) >= self._recently_moved_window:
            self._recently_moved_processes.pop(0)
        self._recently_moved_processes.append(set())

    def _can_move_process(self):
        return self._process_moves_this_frame < MAX_PROCESS_MOVES_PER_FRAME

    def _can_swap_page(self):
        return self._page_swaps_this_frame < MAX_PAGE_SWAPS_PER_FRAME

    def _handle_io_queue(self):
        if self.io_queue.io_count > 0:
            self.do_io()

    def _handle_page_swaps(self):
        for proc in self.processes.values():
            if not self._can_swap_page():
                break
            if proc.waiting_for_page:
                for page in proc.pages:
                    if page.on_disk and not page.swap_in_progress and not page.waiting_to_swap:
                        if page.key not in self._pending_swap_ins:
                            if self._make_room_in_ram():
                                self.move_page(page.pid, page.idx)
                                self._pending_swap_ins.add(page.key)
                                self._page_swaps_this_frame += 1
                        break

    def _make_room_in_ram(self):
        if not self._can_swap_page():
            return False
        for page in self.pages.values():
            if (not page.on_disk and not page.in_use 
                    and not page.swap_in_progress and not page.waiting_to_swap
                    and page.key not in self._pending_swap_outs):
                self.move_page(page.pid, page.idx)
                self._pending_swap_outs.add(page.key)
                self._page_swaps_this_frame += 1
                return True
        return False

    def _handle_terminated_processes(self):
        for proc in list(self.processes.values()):
            if proc.has_ended and proc.has_cpu:
                self.move_process(proc.pid)

    def _schedule_processes(self):
        active_procs = [p for p in self.processes.values() if not p.has_ended]
        running = [p for p in active_procs if p.has_cpu]
        waiting = [p for p in active_procs if not p.has_cpu and not p.waiting_for_io and not p.waiting_for_page and p.starvation_level > 0]
        waiting.sort(key=lambda p: p.starvation_level, reverse=True)
        recently_moved = set()
        for s in self._recently_moved_processes:
            recently_moved.update(s)
        happy_running = [p for p in running if p.starvation_level == 0]
        waiting_to_assign = [p for p in waiting if p.starvation_level > 0]
        for proc in happy_running:
            if not waiting_to_assign:
                break
            if not self._can_move_process():
                break
            if proc.pid in recently_moved:
                continue
            self.move_process(proc.pid)
            self._process_moves_this_frame += 1
            self._recently_moved_processes[-1].add(proc.pid)
            waiting_to_assign.pop(0)
        available_cpus = num_cpus - len(running)
        for proc in waiting_to_assign:
            if available_cpus <= 0:
                break
            if not self._can_move_process():
                break
            if proc.pid in recently_moved:
                continue
            pages_on_disk = [p for p in proc.pages 
                             if p.on_disk and not p.swap_in_progress and not p.waiting_to_swap
                             and p.key not in self._pending_swap_ins]
            if pages_on_disk:
                for page in pages_on_disk:
                    if self._make_room_in_ram():
                        self.move_page(page.pid, page.idx)
                        self._pending_swap_ins.add(page.key)
                continue
            self.move_process(proc.pid)
            self._process_moves_this_frame += 1
            self._recently_moved_processes[-1].add(proc.pid)
            available_cpus -= 1

scheduler = SimpleScheduler()
