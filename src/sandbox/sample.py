"""
Sample config file for the sandbox mode.
Only the `stage` variable is used while setting up the sandbox stage.
It must be an instance of either `Stage` or a subclass of `Stage`.
The `name` and `standalone` properties of `stage` will be overridden.
"""

from config.stage_config import StageConfig
from scenes.stage import Stage

config = StageConfig(
    num_cpus=4,
    num_processes_at_startup=14,
    num_ram_rows=8,
    swap_delay_ms=100,
    parallel_swaps=1,
    new_process_probability=0.05,
    priority_process_probability=0.01,
    io_probability=0.01,
)

stage = Stage('', config)
