from dataclasses import dataclass

from stage_config import StageConfig

@dataclass(frozen=True)
class DifficultyLevel:
    name: str
    config: StageConfig

_easy_difficulty = DifficultyLevel(
    'Easy',
    StageConfig(
        num_cpus=4,
        num_processes_at_startup=14,
        num_ram_rows=8,
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
        num_cpus=8,
        num_processes_at_startup=28,
        num_ram_rows=6,
        new_process_probability=0.1,
        priority_process_probability=0.05,
        io_probability=0.1,
    )
)

_harder_difficulty = DifficultyLevel(
    'Harder',
    StageConfig(
        num_cpus=12,
        num_processes_at_startup=35,
        num_ram_rows=6,
        new_process_probability=0.2,
        priority_process_probability=0.1,
        io_probability=0.2,
    )
)

_insane_difficulty = DifficultyLevel(
    'Insane',
    StageConfig(
        num_cpus=16,
        num_processes_at_startup=42,
        num_ram_rows=4,
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
