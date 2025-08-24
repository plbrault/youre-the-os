from dataclasses import dataclass

@dataclass(frozen=True)
class CpuConfig:
    num_cores: int = 4
    num_threads_per_core: int | list[int] = 1
    process_time_to_happiness_ms: int | list[int] = 5000
    multithread_penalty_ms: int | list[int] = 0

    @property
    def num_threads_for_core(self) -> list[int]:
        if isinstance(self.num_threads_per_core, int):
            return [self.num_threads_per_core] * self.num_cores
        return self.num_threads_per_core

    @property
    def total_threads(self) -> int:
        return sum(self.num_threads_for_core)    

    @property
    def process_time_to_happiness_ms_for_core(self) -> list[int]:
        if isinstance(self.process_time_to_happiness_ms, int):
            return [self.process_time_to_happiness_ms] * self.num_cores
        return self.process_time_to_happiness_ms

    @property
    def multithread_penalty_ms_for_core(self) -> list[int]:
        if isinstance(self.multithread_penalty_ms, int):
            return [self.multithread_penalty_ms] * self.num_cores
        return self.multithread_penalty_ms
