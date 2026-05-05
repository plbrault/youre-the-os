from dataclasses import dataclass, field

from constants import MAX_PROCESSES, ONE_MINUTE
from config.cpu_config import CpuConfig

@dataclass(frozen=True)
class StageConfig:
    cpu_config: CpuConfig = CpuConfig()
    num_processes_at_startup: int = 14
    max_processes: int = MAX_PROCESSES
    max_processes_terminated_by_user: int = 10 # user refers to in-game user, not to the player.
    num_ram_rows: int = 8
    swap_delay_ms: int = 100
    parallel_swaps: int = 1
    new_process_probability: float = 0.05
    priority_process_probability: float = 0.01
    force_new_standard_process_at_times_ms: list[int] = field(default_factory=list)
    force_new_priority_process_at_times_ms: list[int] = field(default_factory=list)
    io_probability: float = 0.01
    priority_process_io_probability: float | None = None
    io_min_waiting_time_ms: int = 1000
    io_max_waiting_time_ms: int = 5000
    graceful_termination_probability: float = 0.01
    priority_process_graceful_termination_probability: float | None = None
    time_ms_to_show_sort_button: int = 6 * ONE_MINUTE
    time_ms_to_show_auto_sort_checkbox: int = 12 * ONE_MINUTE

    def __post_init__(self):
        if self.priority_process_io_probability is None:
            object.__setattr__(self, 'priority_process_io_probability', self.io_probability)
        if self.priority_process_graceful_termination_probability is None:
            object.__setattr__(
                self, 'priority_process_graceful_termination_probability',
                self.graceful_termination_probability)
