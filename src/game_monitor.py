"""GameMonitor

The game monitor is used to gather notifications from game objects
and dispatch them to the automation script.
"""

from enum import Enum
from types import SimpleNamespace

NotificationType = Enum('_nt', [
    'IO_QUEUE',

    'PAGE_NEW',
    'PAGE_USE',
    'PAGE_SWAP_QUEUE',
    'PAGE_SWAP_START',
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


_notifications = []

def _add_notification(typ, data):
    _notifications.append(
        SimpleNamespace(etype=typ.name, **data)
    )

def notify_io_event_count(count):
    _add_notification(NotificationType.IO_QUEUE, {
        'io_count': count
    })

def notify_page_swap_queue(pid, idx, waiting):
    _add_notification(NotificationType.PAGE_SWAP_QUEUE, {
        'pid': pid,
        'idx': idx,
        'waiting': waiting
    })

def notify_page_swap_start(pid, idx):
    _add_notification(NotificationType.PAGE_SWAP_START, {
        'pid': pid,
        'idx': idx
    })

def notify_page_swap(pid, idx, swap):
    _add_notification(NotificationType.PAGE_SWAP, {
        'pid': pid,
        'idx': idx,
        'swap': swap
    })

def notify_page_new(pid, idx, swap, use):
    _add_notification(NotificationType.PAGE_NEW, {
        'pid': pid,
        'idx': idx,
        'swap': swap,
        'use': use
    })

def notify_page_use(pid, idx, use):
    _add_notification(NotificationType.PAGE_USE, {
        'pid': pid,
        'idx': idx,
        'use': use
    })

def notify_page_free(pid, idx):
    _add_notification(NotificationType.PAGE_FREE, {
        'pid': pid,
        'idx': idx
    })

def notify_process_wait_page(pid, value):
    _add_notification(NotificationType.PROC_WAIT_PAGE, {
        'pid': pid,
        'waiting_for_page': value
    })

def notify_process_wait_io(pid, value):
    _add_notification(NotificationType.PROC_WAIT_IO, {
        'pid': pid,
        'waiting_for_io': value
    })

def notify_process_terminated(pid):
    _add_notification(NotificationType.PROC_TERM, {
        'pid': pid
    })

def notify_process_killed(pid):
    _add_notification(NotificationType.PROC_KILL, {
        'pid': pid
    })

def notify_process_starvation(pid, level, time_to_termination):
    _add_notification(NotificationType.PROC_STARV, {
        'pid' : pid,
        'starvation_level': level,
        'time_to_termination': time_to_termination
    })

def notify_process_new(pid):
    _add_notification(NotificationType.PROC_NEW, {
        'pid': pid
    })

def notify_process_cpu(pid, cpu):
    _add_notification(NotificationType.PROC_CPU, {
        'pid': pid,
        'cpu': cpu
    })

def notify_process_end(pid):
    _add_notification(NotificationType.PROC_END, {
        'pid': pid
    })


def get_notifications():
    return _notifications

def clear_notifications():
    _notifications.clear()
