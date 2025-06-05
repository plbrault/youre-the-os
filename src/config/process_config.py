from dataclasses import dataclass

from constants import MAX_PROCESSES, ONE_MINUTE

@dataclass(frozen=True)
class ProcessConfig:
    io_probability: float
    graceful_termination_probability: float
    time_between_starvation_levels_ms: int
