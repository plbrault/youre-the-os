from dataclasses import dataclass

from constants import SWAP_DELAY_NAMES_TO_MS
from config.cpu_config import CpuConfig
from config.stage_config import StageConfig

@dataclass(frozen=True)
class DifficultyLevel:
    name: str
    config: StageConfig

_easy_difficulty = DifficultyLevel(
    'Easy',
    StageConfig(
        cpu_config=CpuConfig(num_cores=4),
        num_processes_at_startup=14,
        num_ram_rows=8,
        swap_delay_ms=SWAP_DELAY_NAMES_TO_MS['Low'],
        parallel_swaps=1,
        new_process_probability=0.05,
        priority_process_probability=0.01,
        io_probability=0.01,
    )
)

_normal_difficulty = DifficultyLevel(
    'Normal',
    StageConfig()
)

_hard_difficulty = DifficultyLevel(
    'Hard',
    StageConfig(
        cpu_config=CpuConfig(num_cores=8),
        num_processes_at_startup=28,
        num_ram_rows=6,
        swap_delay_ms=SWAP_DELAY_NAMES_TO_MS['Medium'],
        parallel_swaps=4,
        new_process_probability=0.1,
        priority_process_probability=0.05,
        io_probability=0.1,
    )
)

_harder_difficulty = DifficultyLevel(
    'Harder',
    StageConfig(
        cpu_config=CpuConfig(num_cores=12),
        num_processes_at_startup=35,
        num_ram_rows=6,
        swap_delay_ms=SWAP_DELAY_NAMES_TO_MS['High'],
        parallel_swaps=8,
        new_process_probability=0.2,
        priority_process_probability=0.1,
        io_probability=0.2,
    )
)

_insane_difficulty = DifficultyLevel(
    'Insane',
    StageConfig(
        cpu_config=CpuConfig(num_cores=16),
        num_processes_at_startup=42,
        num_ram_rows=4,
        swap_delay_ms=SWAP_DELAY_NAMES_TO_MS['Higher'],
        parallel_swaps=16,
        new_process_probability=1,
        priority_process_probability=0.1,
        io_probability=0.3,
    )
)

difficulty_levels = [
    _easy_difficulty,
    _normal_difficulty,
    _hard_difficulty,
    _harder_difficulty,
    _insane_difficulty
]

difficulty_levels_map = {
    level.name.lower(): level for level in difficulty_levels
}

default_difficulty = _normal_difficulty
