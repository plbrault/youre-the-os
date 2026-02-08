from automation import Scheduler

class SimpleScheduler(Scheduler):
    def schedule(self):
        self._pending_swap_outs = set()
        self._pending_swap_ins = set()
        self._handle_io_queue()
        self._handle_page_swaps()
        self._handle_terminated_processes()
        self._schedule_processes()

    def _handle_io_queue(self):
        if self.io_queue.io_count > 0:
            self.do_io()

    def _handle_page_swaps(self):
        for proc in self.processes.values():
            if proc.waiting_for_page:
                for page in proc.pages:
                    if page.on_disk and not page.swap_in_progress and not page.waiting_to_swap:
                        if page.key not in self._pending_swap_ins:
                            if self._make_room_in_ram():
                                self.move_page(page.pid, page.idx)
                                self._pending_swap_ins.add(page.key)
                        break

    def _make_room_in_ram(self):
        for page in self.pages.values():
            if (not page.on_disk and not page.in_use 
                    and not page.swap_in_progress and not page.waiting_to_swap
                    and page.key not in self._pending_swap_outs):
                self.move_page(page.pid, page.idx)
                self._pending_swap_outs.add(page.key)
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
            available_cpus -= 1

scheduler = SimpleScheduler()
