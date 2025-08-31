from dataclasses import dataclass
from enum import Enum

CoreType = Enum('CoreType', [
    'STANDARD',
    'PERFORMANCE',
    'EFFICIENT'
])

@dataclass(frozen=True)
class CpuConfig:
    """Configuration of physical cores and logical cores (threads) of the CPU.

    An attribute expressed as a single value applies to all cores.
    An attribute expressed as a list applies to each core in order.

    Each thread will translate to a Cpu object in-game, as an OS would typically see it.
    """

    num_cores: int = 4
    core_types: CoreType | list[CoreType] = CoreType.STANDARD
    num_threads_per_core: int | list[int] = 1
    process_happiness_ms: int | list[int] = 5000

    """Extra time added to process_happiness_ms when
       multiple processes are running on the same physical core."""
    penalty_ms: int | list[int] = 0

    @property
    def num_threads_for_core(self) -> list[int]:
        if isinstance(self.num_threads_per_core, int):
            return [self.num_threads_per_core] * self.num_cores
        return self.num_threads_per_core

    @property
    def total_threads(self) -> int:
        return sum(self.num_threads_for_core)

    @property
    def process_happiness_ms_for_core(self) -> list[int]:
        if isinstance(self.process_happiness_ms, int):
            return [self.process_happiness_ms] * self.num_cores
        return self.process_happiness_ms

    @property
    def penalty_ms_for_core(self) -> list[int]:
        if isinstance(self.penalty_ms, int):
            return [self.penalty_ms] * self.num_cores
        return self.penalty_ms

    @property
    def type_for_core(self) -> list[CoreType]:
        if isinstance(self.core_types, CoreType.__class__):
            return [self.core_types] * self.num_cores
        return self.core_types
