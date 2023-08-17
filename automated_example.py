#
# an example on a script to run an automated scheduler
#

import random

#
# globals passed are:
#
# `num_cpus` number of available CPUs
# `num_ram_pages` number of pages that fit on RAM
# `num_swap_pages` number of pages that fit on SWAP
#

#
# constants are passed as the enum type:
#	'IO_QUEUE',
#	'PAGE_NEW',
#	'PAGE_USE',
#	'PAGE_SWAP',
#   'PAGE_FREE',
#	'PROC_NEW',
#	'PROC_CPU',
#	'PROC_STARV',
#	'PROC_WAIT_IO',
#	'PROC_WAIT_PAGE',
#	'PROC_TERM',
#	'PROC_KILL'

#
# a process is identified by its PID
#
# a memory page are identified by the owner's PID
# and an index IDX inside the process
# (first page is idx=0, second page is idx=1, etc...)

#
# helper functions to generate actions
#

# to move a process to/from CPU
def move_process(pid):
    return {
        'type': 'process',
        'pid': pid
    }

# to move a page to/from SWAP
def move_page(pid, idx):
    return {
        'type': 'page',
        'pid': pid,
        'idx': idx
    }

# to direct IO to processes
def do_io():
    return {'type': 'io_queue'}

# keep track of list of processes
# list of pids
procs = []
in_cpu = []
wait_io = []
wait_page = []

# keep track of starvating processes
starving = []

# to keep track of where pages are
# list of (pid, idx)
ram_pages = []
swap_pages = []


#
# the main entrypoint to run the scheduler
#
# it receives a list of events generated from processes/pages
# see `src/lib/event_manager` for generated events
#
# it should return a list of events to happen
#
def run_os(generated_events: list) -> list:

    global procs
    global in_cpu
    global wait_io
    global starving
    global ram_pages
    global swap_pages

    to_return = []

    for e in generated_events:
        if e.etype == IO_QUEUE:
            if e.io_count > 0:
                to_return.append(do_io())
        if e.etype == PAGE_NEW:
            t = swap_pages if e.swap else ram_pages
            t.append( (e.pid, e.idx) )
        elif e.etype == PAGE_USE:
            if e.use == True and (e.pid, e.idx) in swap_pages:
                # find some page in RAM that is not being used
                for page in ram_pages:
                    if page[0] not in in_cpu:
                        # good enough
                        to_return.append(move_page(*page))
                        break
                to_return.append(move_page(e.pid, e.idx))
        elif e.etype == PAGE_SWAP:
            f,t = (ram_pages,swap_pages) if e.swap else (swap_pages, ram_pages)
            f.remove((e.pid, e.idx))
            t.append((e.pid, e.idx))
        elif e.etype == PAGE_FREE:
            try:
                swap_pages.remove((e.pid, e.idx))
            except ValueError:
                ram_pages.remove((e.pid, e.idx))
        elif e.etype == PROC_NEW:
            procs.append(e.pid)
            if len(in_cpu) < num_cpus:
                to_return.append(move_process(e.pid))
        elif e.etype == PROC_CPU:
            if e.cpu:
                in_cpu.append(e.pid)
            else:
                in_cpu.remove(e.pid)
        elif e.etype == PROC_STARV:
            if e.starvation_level == 0 and e.pid in in_cpu:
                # remove from cpu, get another in there
                to_return.append(move_process(e.pid))
                # find a random one to put in CPU
                try:
                    pid = random.choice(starving)
                    starving.remove(pid)
                except IndexError:
                    pid = random.choice(procs)
                    while pid in in_cpu:
                        pid = random.choice(procs)
                to_return.append(move_process(pid))
            elif e.starvation_level > 0 and e.pid not in starving:
                starving.append(e.pid)
        elif e.etype == PROC_TERM:
            procs.remove(e.pid)
            # remove from cpu, get another in there
            to_return.append(move_process(e.pid))
            # find a random one to put in CPU
            for pid in random.sample(procs, k=len(procs)):
                if pid not in in_cpu:
                    to_return.append(move_process(pid))
        elif e.etype == PROC_KILL:
            procs.remove(e.pid)
        elif e.etype in (PROC_WAIT_IO, PROC_WAIT_PAGE):
            # not handled in example
            pass
    return to_return
