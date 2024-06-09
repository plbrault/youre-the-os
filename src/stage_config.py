from dataclasses import dataclass

from constants import MAX_PROCESSES

@dataclass(frozen=True)
class StageConfig:
    num_cpus: int = 4
    num_processes_at_startup: int = 14
    max_processes: int = MAX_PROCESSES
    num_ram_rows: int = 8
    new_process_probability: float = 0.05
    priority_process_probability: float = 0.01
    io_probability: float = 0.01
    graceful_termination_probability: float = 0.01
