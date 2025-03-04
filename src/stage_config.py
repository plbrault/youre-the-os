from dataclasses import dataclass

from constants import MAX_PROCESSES, ONE_MINUTE

@dataclass(frozen=True)
class StageConfig:
    num_cpus: int = 4
    num_processes_at_startup: int = 14
    max_processes: int = MAX_PROCESSES
    max_processes_terminated_by_user: int = 10 # user refers to in-game user, not to the player.
    num_ram_rows: int = 8
    swap_delay_ms: int = 100
    parallel_swaps: int = 4
    new_process_probability: float = 0.05
    priority_process_probability: float = 0.01
    io_probability: float = 0.01
    graceful_termination_probability: float = 0.01
    time_ms_to_show_sort_button: int = 6 * ONE_MINUTE
    time_ms_to_show_auto_sort_checkbox: int = 12 * ONE_MINUTE
