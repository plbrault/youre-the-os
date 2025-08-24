from dataclasses import dataclass

@dataclass(frozen=True)
class CpuConfig:
    threads: int = 1
    time_to_process_happiness_ms: int = 5000
    multithread_penalty_ms: int = 0

STANDARD_CPU = CpuConfig()
HYPERTHREADING_CPU = CpuConfig(threads=2, time_to_process_happiness_ms=5000, multithread_penalty_ms=1000)
