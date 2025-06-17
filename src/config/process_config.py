from dataclasses import dataclass

@dataclass(frozen=True)
class ProcessConfig:
    io_probability: float
    graceful_termination_probability: float
    time_between_starvation_levels_ms: int
