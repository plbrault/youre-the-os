from dataclasses import dataclass

@dataclass(frozen=True)
class PageConfig:
    swap_delay_ms: int
    parallel_swaps: int
