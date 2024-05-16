"""GameMonitor

The game monitor is used to gather events from game objects
and dispatch them to the automation script.
"""

from enum import Enum
from types import SimpleNamespace

# event types
etypes = Enum('_et', [
    'IO_QUEUE',

    'PAGE_NEW',
    'PAGE_USE',
    'PAGE_SWAP',
    'PAGE_FREE',

    'PROC_NEW',
    'PROC_CPU',
    'PROC_STARV',
    'PROC_WAIT_IO',
    'PROC_WAIT_PAGE',
    'PROC_TERM',
    'PROC_KILL',
    'PROC_END'
])


_events = []

def add_event(typ, data):
    _events.append(
        SimpleNamespace(etype=typ.name, **data)
    )

def event_io_queue(count):
    add_event(etypes.IO_QUEUE, {
        'io_count': count
    })

def event_page_swap(pid, idx, swap):
    add_event(etypes.PAGE_SWAP, {
        'pid': pid,
        'idx': idx,
        'swap': swap
    })

def event_page_new(pid, idx, swap, use):
    add_event(etypes.PAGE_NEW, {
        'pid': pid,
        'idx': idx,
        'swap': swap,
        'use': use
    })

def event_page_use(pid, idx, use):
    add_event(etypes.PAGE_USE, {
        'pid': pid,
        'idx': idx,
        'use': use
    })

def event_page_free(pid, idx):
    add_event(etypes.PAGE_FREE, {
        'pid': pid,
        'idx': idx
    })

def event_process_wait_page(pid, value):
    add_event(etypes.PROC_WAIT_PAGE, {
        'pid': pid,
        'waiting_for_page': value
    })

def event_process_wait_io(pid, value):
    add_event(etypes.PROC_WAIT_IO, {
        'pid': pid,
        'waiting_for_io': value
    })

def event_process_terminated(pid):
    add_event(etypes.PROC_TERM, {
        'pid': pid
    })

def event_process_killed(pid):
    add_event(etypes.PROC_KILL, {
        'pid': pid
    })

def event_process_starvation(pid, level):
    add_event(etypes.PROC_STARV, {
        'pid' : pid,
        'starvation_level': level
    })

def event_process_new(pid):
    add_event(etypes.PROC_NEW, {
        'pid': pid
    })

def event_process_cpu(pid, cpu):
    add_event(etypes.PROC_CPU, {
        'pid': pid,
        'cpu': cpu
    })

def event_process_end(pid):
    add_event(etypes.PROC_END, {
        'pid': pid
    })


def get_events():
    return _events

def clear_events():
    _events.clear()
